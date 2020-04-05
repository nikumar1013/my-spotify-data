#!/usr/bin/env python

import bisect
import operator

import numpy as np
import numpy.ma as ma
from pydap.client import open_url
import pydap.lib
pydap.lib.CACHE = '.cache'
from coards import from_udunits, to_udunits

# distance weight for interpolation; this could be 2 for quadratic distance, eg
WEIGHT = 1


__all__ = ['extract_point', 'MOM3', 'MOM4p1', 'PIRATA_Profile', 'ARGO_Profile',
           'select_profiles', 'build_exp', 'nrmsd', 'cvrmsd', 'rmsd', 'bias',
           'correlation', 'load_data']


def seconds(tdelta):
    return tdelta.days * 3600 + tdelta.seconds


def extract_point(model, ctd):

    # load model data
    field, depth = model.field, model.depth
    lon, lat = model.lon, model.lat
    time = [from_udunits(v[0], v[1]) for v in model.time]

    # load ctd data and extract positions
    t = from_udunits(ctd.time[0], ctd.time[1])
    y = ctd.lat

    #x = ctd.lon % 360
    if model.name == 'MOM3':
        x = ctd.lon + 360
    else:
        x = ctd.lon

    if x > lon[-1]:
        x += lon[0]
    if x < lon[0]:
        x += lon[-1]

    # find the horizontal position and time for this CTD measure
    i0 = np.searchsorted(lon, x, side='left') - 1
    j0 = np.searchsorted(lat, y, side='left') - 1
    l0 = np.searchsorted(time, t, side='left') - 1

    if i0 < 0:
        i0 = 0
    if j0 < 0:
        j0 = 0
    if l0 < 0:
        l0 = 0

    # prefetching the data, avoid comm overhead
    data = model.get_data(l0, j0, i0)
    values = []
    for z in -ctd.depth[:-1]:
        # for each point find the 8 encompassing points and calculate
        # weighted average
        k0 = bisect.bisect(depth, z) - 1
        if k0 < 0:
            k0 = 0
        if k0 >= len(depth):
            values.append(field.missing_value)

        v0 = w = 0
        v1 = w = 0
        for (i, j, k) in ((i, j, k) for i in (0, 1)
                                    for j in (0, 1)
                                    for k in (k0, k0 + 1)):
            distance = np.sqrt((x - lon[i0 + i]) ** 2 + (y - lat[j0 + j]) ** 2
                + (z - depth[k]) ** 2)
            if not np.all(data[:, k, j, i].mask):
                v0 += float(data[0, k, j, i]) / (distance ** WEIGHT)
                v1 += float(data[1, k, j, i]) / (distance ** WEIGHT)
                w += 1 / (distance ** WEIGHT)
        if w:
            v0 /= w
            v1 /= w

        # interpolate linearly in time
        v = (v0 + (v1 - v0) *
            seconds(t - time[l0]) / seconds(time[l0 + 1] - time[l0]))
        values.append(v)
    return ma.masked_equal(np.array(values), field.missing_value)


def extract_cruise(model, data, fields):
    lons = np.zeros(len(data))
    lats = np.zeros(len(data))
    modelmeasures = []
    datameasures = []
    depthmeasures = []
    timemeasures = []
    for i, measure in enumerate(data):
        # get the lat/lon of each cruise stop
        lats[i] = measure.lat
        lons[i] = measure.lon

        modelvalues = []
        datavalues = []
        for modelfield, datafield in fields:
            model.field = modelfield
            measure.field = datafield
            yi = extract_point(model, measure)
            modelvalues.append(yi)

            try:
                measure.field.missing_value
            except AttributeError:
                dv = ma.masked_array(np.array(measure.data[:-1]))
            else:
                dv = ma.masked_equal(
                        np.array(measure.data[:-1]),
                        measure.field.missing_value)
            datavalues.append(dv)

        modelmeasures.append(modelvalues)
        datameasures.append(datavalues)
        depthmeasures.append(measure.depth[:-1])
        timemeasures.append(measure.time)

    return (lons, lats, modelmeasures,
            datameasures, depthmeasures, timemeasures)


class Model(object):

    def __init__(self, urlpath):
        self.data = open_url(urlpath)
        self._field = None

    @property
    def field(self):
        return self._field

    @field.setter
    def field(self, field):
        self._field = self.data[field]

    @property
    def lon(self):
        LON = self.field.dimensions[-1]
        return self.data[LON][:]

    @property
    def lat(self):
        LAT = self.field.dimensions[-2]
        return self.data[LAT][:]

    @property
    def depth(self):
        DEPTH = self.field.dimensions[-3]
        return self.data[DEPTH][:]

    @property
    def time(self):
        TIME = self.field.dimensions[-4]
        return [(v, self.data[TIME].units) for v in self.data[TIME][:]]


class MOM4p1(Model):

    def __init__(self, urlpath):
        super(MOM4p1, self).__init__(urlpath)
        self.name = 'MOM4p1'

    def get_data(self, l0, j0, i0):
        return ma.masked_equal(
                self.field.array[l0:l0 + 2, :, j0:j0 + 2, i0:i0 + 2],
                self.field.missing_value)


class MOM3(Model):

    def __init__(self, urlpath):
        super(MOM3, self).__init__(urlpath)
        self.name = 'MOM3'

    @property
    def time(self):
        TIME, = self.field.dimensions[-4]
        # this is a fix for MOM3 output which has broken time axis
        return [(v, self.data[TIME].units)
                for v in np.cumsum(self.data[TIME][:])]


class Measure(object):

    def __init__(self, dataurl, indexurl, pid=None):
        self._data = open_url(dataurl)
        self._field = None
        self.index = open_url(indexurl)
        self.pid = pid
        d = self._data.sequence[self._data.sequence.profile == self.pid]
        self.depthdata = d

    @property
    def lat(self):
        return float(list(self.geodata.latitude)[0])

    @property
    def lon(self):
        return float(list(self.geodata.longitude)[0])

    @property
    def depth(self):
        raise NotImplementedError

    @property
    def time(self):
        d = self.geodata.time
        t = (list(d)[0], d.units)
        return t

    @property
    def field(self):
        return self._field

    @field.setter
    def field(self, field):
        self._field = self.depthdata[field]

    @property
    def data(self):
        return np.array(list(self._field))


class ARGO_Profile(Measure):

    def __init__(self, dataurl, indexurl, pid=None):
        super(ARGO_Profile, self).__init__(dataurl, indexurl, pid)
        self.name = 'ARGO'
        g = self.index.sequence[self.index.sequence.profile == self.pid]
        self.geodata = g

    @property
    def depth(self):
        # TODO: convert this! Gui said it was a good aproximation for now
        # just to return the pressure (1 bar = 10 m)
        return -(np.array(list(self.depthdata.pressure)) / 10.)


class PIRATA_Profile(Measure):

    def __init__(self, dataurl, indexurl, pid=None):
        super(PIRATA_Profile, self).__init__(dataurl, indexurl, pid)
        self.name = 'PIRATA'
        g = self.index.sequence[self.index.sequence.profileid == self.pid]
        self.geodata = g

    @property
    def depth(self):
        return np.array(list(self.depthdata.depth))


def select_profiles(indexurl, begin=None, end=None,
                    urcrnrlat=None, urcrnrlon=None,
                    llcrnrlat=None, llcrnrlon=None):
    index = open_url(indexurl)
    begin = to_udunits(begin, index.sequence.time.units)
    end = to_udunits(end, index.sequence.time.units)

    conds = []
    if begin:
        c = (index.sequence.time > begin) & (index.sequence.time < end)
        conds.append(c)
    if urcrnrlat:
        c = ((index.sequence.latitude > llcrnrlat) &
             (index.sequence.latitude < urcrnrlat) &
             (index.sequence.longitude > llcrnrlon) &
             (index.sequence.longitude < urcrnrlon))
        conds.append(c)

    prof_ids = index.sequence[reduce(operator.__and__, conds)]
    return prof_ids


def correlation(crds1, crds2):
    assert(crds1.shape == crds2.shape)
    coef = np.corrcoef(crds1, crds2)
    try:
        return coef[0,-1]
    except IndexError:
        return None


def bias(model, measure):
    assert(model.shape == measure.shape)
    return np.median(model - measure)


def rmsd(crds1, crds2):
    assert(crds1.shape == crds2.shape)

    n_vec = np.shape(crds1)[0]
    E0 = np.sum((crds1 - crds2) ** 2)
    rmsd_sq = E0 / float(n_vec)
    rmsd_sq = max([rmsd_sq, 0.0])
    return np.sqrt(rmsd_sq)


def cvrmsd(crds1, crds2):
    return rmsd(crds1, crds2) / np.mean(crds2)


def nrmsd(crds1, crds2):
    try:
        return rmsd(crds1, crds2) / (np.max(crds2) - np.min(crds2))
    except ValueError:
        return None


def get_data(model, cruise, exps):
    fields = [(exp['model_field'], exp['ctd_var']) for exp in exps]
    return extract_cruise(model, cruise, fields)


def build_exp(*args, **kwargs):
    exp = {}
    exp.update(kwargs)
    exp['ctd_unit_conversion'] = kwargs.get('ctd_unit_conversion', lambda x: x)
    exp['model_unit_conversion'] = kwargs.get('model_unit_conversion',
                                              lambda x: x)
    return exp


def load_data(model, cruise, exps, cache=None):
    if cache is None:
        cache = {}

    if not cache.keys():
        (lons,
         lats,
         values_model,
         values_ctd,
         values_depth,
         values_time) = get_data(model, cruise, exps)
        cache['lons'] = lons
        cache['lats'] = lats
        cache['model'] = values_model
        cache['ctd'] = values_ctd
        cache['depth'] = values_depth
        cache['time'] = values_time

    try:
        cache.sync()
    except AttributeError:
        pass

    return cache
