"""Dolphot Explorer Bokeh Figure and Widgets"""
import os
import itertools
import sys

import pandas as pd
import numpy as np

from astropy.table import Table

from bokeh.layouts import row, widgetbox
from bokeh.models import Select, Slider
from bokeh.models.widgets import CheckboxButtonGroup, RangeSlider
from bokeh.palettes import Spectral5
from bokeh.plotting import curdoc, figure, gridplot


def minmax(d, dparam):
    """
    Return minimum and maxium of all colums with dparam
    e.g., dparam='SNR' would return min and max of concatenated arrrays
    F475W_SNR, F814W_SNR, etc.

    Paramaters
    ----------
    d : pd.DataFrame
    dparam : str
        dolphot parameter (SNR, CHI, any string that exists in d.columns)

    Returns
    -------
    min, max of concatenated array
    """
    arr = np.concatenate([d[c] for c in list(d.columns) if dparam in c])
    return np.min(arr), np.max(arr)


def limit_data():
    """Slice data by dolphot values and recovered stars in two filters"""
    fmt = '{:s}_{:s}'
    filter1, filter2 = filters.value.split(',')
    selected = data[
        (np.abs(data[fmt.format(filter1, 'VEGA')]) <= 60) &
        (np.abs(data[fmt.format(filter2, 'VEGA')]) <= 60) &
        (data[fmt.format(filter1, 'SNR')] <= snr.value[1]) &
        (data[fmt.format(filter1, 'SNR')] >= snr.value[0]) &
        (data[fmt.format(filter1, 'SHARP')] <= shp.value[1]) &
        (data[fmt.format(filter1, 'SHARP')] >= shp.value[0]) &
        (data[fmt.format(filter1, 'CROWD')] <= cwd.value[1]) &
        (data[fmt.format(filter1, 'CROWD')] >= cwd.value[0]) &
        (data[fmt.format(filter1, 'ROUND')] <= rnd.value[1]) &
        (data[fmt.format(filter1, 'ROUND')] >= rnd.value[0]) &
        (data[fmt.format(filter1, 'ERR')] <= err.value[1]) &
        (data[fmt.format(filter1, 'ERR')] >= err.value[0]) &
        (data[fmt.format(filter1, 'CHI')] <= chi.value[1]) &
        (data[fmt.format(filter1, 'CHI')] >= chi.value[0]) &

        (data[fmt.format(filter2, 'SNR')] <= snr.value[1]) &
        (data[fmt.format(filter2, 'SNR')] >= snr.value[0]) &
        (data[fmt.format(filter2, 'SHARP')] <= shp.value[1]) &
        (data[fmt.format(filter2, 'SHARP')] >= shp.value[0]) &
        (data[fmt.format(filter2, 'CROWD')] <= cwd.value[1]) &
        (data[fmt.format(filter2, 'CROWD')] >= cwd.value[0]) &
        (data[fmt.format(filter2, 'ROUND')] <= rnd.value[1]) &
        (data[fmt.format(filter2, 'ROUND')] >= rnd.value[0]) &
        (data[fmt.format(filter2, 'ERR')] <= err.value[1]) &
        (data[fmt.format(filter2, 'ERR')] >= err.value[0]) &
        (data[fmt.format(filter2, 'CHI')] <= chi.value[1]) &
        (data[fmt.format(filter2, 'CHI')] >= chi.value[0])]
    return selected


def create_figure(xflipped=False, yflipped=False, cmd=True):
    """Create Bokeh figure"""
    COLORS = Spectral5
    # Apply data slicing
    df = limit_data()

    xs = df[x.value].values
    ys = df[y.value].values

    # data ranges
    xdr = (xs.min(), xs.max())
    ydr = (ys.min(), ys.max())
    if xflipped:
        xdr = (xs.max(), xs.min())
    if yflipped:
        ydr = (ys.max(), ys.min())

    plt_kw = {'plot_height': 600,
              'plot_width':800,
              'output_backend': "webgl",
              'x_range': xdr,
              'y_range': ydr,
              'tools': "pan,zoom_in,zoom_out,box_zoom,box_select,reset,save"}

    c = "#31AADE"  # default color if no color-by selection
    if color.value != 'None':  # odd that bokeh needs 'None' not None...
        groups = pd.qcut(df[color.value].values, len(COLORS), duplicates='drop')
        c = [COLORS[xx] for xx in groups.codes]

    sca_kw = {'color': c,
              'size': size.value,
              'alpha': 0.6,
              'line_color': 'white'}

    p = figure(title=target, **plt_kw)
    p.xaxis.axis_label = x.value
    p.yaxis.axis_label = y.value
    p.scatter(x=xs, y=ys, **sca_kw)

    if cmd:
        magstr = '{}_VEGA'.format(filters.value.split(',')[1])
        colstr = '-'.join(filters.value.split(','))
        mag = df[magstr].values
        col = df[colstr].values
        plt_kw['x_range'] = (col.min(), col.max())
        plt_kw['y_range'] = (mag.max(), mag.min())

        p2 = figure(title='Color-Mag Diagram', **plt_kw)
        p2.xaxis.axis_label = colstr
        p2.yaxis.axis_label = magstr
        p2.scatter(x=col, y=mag, **sca_kw)
        p = gridplot([[p, p2]])

    return p


def update(attr, old, new):
    layout.children[1] = create_figure()
    return


def invert_axes_handler(option):
    xflipped = False
    yflipped = False

    if 0 in option:
        xflipped = True
    if 1 in option:
        yflipped = True

    data = limit_data()
    layout.children[1] = create_figure(xflipped=xflipped,
                                       yflipped=yflipped)
    return


def load_data(fitsfile=None):
    """load fitsfile into pandas DataFrame and extract the target name"""
    # This should use requests someday, or allow for user upload.
    if fitsfile is None:
        base = "./gst"
        # base = "../dolphot-explorer/gst/"
        files = [os.path.join(base, l) for l in os.listdir(base)
                 if l.endswith('fits')]

        filename, = [f for f in files if 'HODGE6.gst.fits' in f]
    else:
        filename = fitsfile

    target = os.path.split(filename)[1].split('.gst')[0]

    t = Table.read(filename, format='fits')
    df = t.to_pandas()
    return df, target


fitsfile = None
if len(sys.argv) > 1:
    fitsfile = sys.argv[1]
    assert fitsfile.lower().endswith('fits'), 'File must have a fits extension'
    assert os.path.isfile(fitsfile), '{0:s} not found'

data, target = load_data(fitsfile)

filters = [f.replace('_VEGA', '') for f in list(data.columns) if 'VEGA' in f]
filters = [f for f in filters if f.endswith('W')]  # excludes narrow bands

# Add two filter combinations (color) to the DataFrame
filter_combos = []
for f1, f2 in itertools.combinations(filters, 2):
    fc = ','.join([f1, f2])
    data['{}-{}'.format(f1, f2)] = \
        data['{}_VEGA'.format(f1)] - data['{}_VEGA'.format(f2)]
    filter_combos.append(fc)

columns = list(data.columns)

d = data.copy()
# cull a copy for only recovered stars to initialize dolphot param limits
for k in filters:
    d = d[d[k + '_VEGA'] < 90].copy()

snrs, snre = minmax(d, 'SNR')
_, erre = minmax(d, 'ERR')
errs = 0
shps, shpe = minmax(d, 'SHARP')
rnds, rnde = minmax(d, 'ROUND')
cwds, cwde = minmax(d, 'CROWD')
chis, chie = minmax(d, 'CHI')

filter2 = filter_combos[0].split(',')[1]  # default filter for left plot
x = Select(title='x-axis', value='{:s}_VEGA'.format(filter2),
           options=columns)
y = Select(title='y-axis', value='{:s}_ERR'.format(filter2),
           options=columns)

color = Select(title='color by', value='None', options=['None'] + columns)

size = Slider(start=0.1, end=10, value=4, step=.1, title="marker size")

filters = Select(title='filter combination', value=filter_combos[0],
                 options=filter_combos)

snr = RangeSlider(start=snrs, end=snre,
                  value=(snrs, snre),
                  step=1, title="SNR range")

err = RangeSlider(start=errs, end=erre,
                  value=(errs, erre),
                  step=.05, title="ERR range")

shp = RangeSlider(start=shps, end=shpe,
                  value=(shps, shpe),
                  step=.1, title="SHARP range")

rnd = RangeSlider(start=rnds, end=rnde,
                  value=(rnds, rnde),
                  step=.1, title="ROUND range")

cwd = RangeSlider(start=cwds, end=cwde,
                  value=(cwds, cwde),
                  step=.1, title="CROWD range")

chi = RangeSlider(start=cwds, end=cwde,
                  value=(chis, chie),
                  step=.1, title="CHI range")

ctrls = [filters, x, y, color, size, snr, err, shp, rnd, cwd, chi]
for ctrl in ctrls:
    ctrl.on_change('value', update)

invert_buttons = CheckboxButtonGroup(labels=["Invert x-axis",
                                             "Invert y-axis"], active=[])
invert_buttons.on_click(invert_axes_handler)

controls = widgetbox([filters, x, y, color, size, invert_buttons,
                      snr, err, shp, rnd, cwd, chi], width=200)

layout = row(controls, create_figure())

curdoc().add_root(layout)
curdoc().title = "DOLPHOT Parameter Explorer"
