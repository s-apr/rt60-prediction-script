# -*- coding: utf-8 -*-
"""
Created on Fri Aug 22 14:26:00 2025

@author: maxbu
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, RadioButtons

#freqs, coefs, sizes
#coefs are from:
#https://www.engineeringtoolbox.com/sound-absorption-coefficients-d_685.html

FREQUENCIES = np.array([125, 250, 500, 1000, 2000, 4000])
ABSORPTION_COEFFICIENTS = {
    'Concrete':         np.array([0.02, 0.03, 0.03, 0.03, 0.04, 0.07]),
    'Drywall':          np.array([0.29, 0.10, 0.05, 0.04, 0.07, 0.09]),
    'Glass':            np.array([0.35, 0.25, 0.18, 0.12, 0.07, 0.04]),
    'Carpet':           np.array([0.02, 0.06, 0.14, 0.37, 0.60, 0.65]),
    'Acoustic Panel':   np.array([0.20, 0.80, 1.00, 1.00, 1.00, 0.90]),
}
ROOM_SIZES = {
    'Small':  {'l': 4, 'w': 3, 'h': 2.5},
    'Medium': {'l': 7, 'w': 5, 'h': 2.8},
    'Large':  {'l': 15, 'w': 10, 'h': 4},
}
MATERIALS = list(ABSORPTION_COEFFICIENTS.keys())


#rt60
def calculate_rt60(l, w, h, material_config):
    #Sabine formula for each freq band
    volume = l * w * h
    area_floor_ceil = l * w
    area_walls_1 = l * h
    area_walls_2 = w * h
    
    alpha_floor = ABSORPTION_COEFFICIENTS[material_config['floor']]
    alpha_ceil = ABSORPTION_COEFFICIENTS[material_config['ceiling']]
    alpha_walls = ABSORPTION_COEFFICIENTS[material_config['walls']]
    
    total_absorption = (
        area_floor_ceil * alpha_floor +
        area_floor_ceil * alpha_ceil +
        2 * (area_walls_1 + area_walls_2) * alpha_walls
    )
    total_absorption[total_absorption == 0] = 1e-6
    rt60 = (0.161 * volume) / total_absorption
    return rt60


fig, ax = plt.subplots(figsize=(12, 8))
plt.subplots_adjust(left=0.1, right=0.55, bottom=0.1, top=0.9)

#init calc
initial_dims = ROOM_SIZES['Medium']
initial_config = {'floor': 'Carpet', 'ceiling': 'Drywall', 'walls': 'Drywall'}
rt60_initial = calculate_rt60(initial_dims['l'], initial_dims['w'], initial_dims['h'], initial_config)

#main plot
line, = ax.plot(FREQUENCIES, rt60_initial, 'o-', lw=2)
ax.set_xscale('log')
ax.set_xticks(FREQUENCIES, [f'{f}Hz' for f in FREQUENCIES])
ax.set_xlabel('Frequency Band')
ax.set_ylabel('RT60 (seconds)')
ax.set_title('Interactive RT60 Calculator')
ax.set_ylim(0, 4)
ax.grid(True, which='both')


#sliders
ax_sliders_l = plt.axes([0.65, 0.80, 0.25, 0.03])
ax_sliders_w = plt.axes([0.65, 0.75, 0.25, 0.03])
ax_sliders_h = plt.axes([0.65, 0.70, 0.25, 0.03])
ax_radio_size = plt.axes([0.65, 0.55, 0.25, 0.12])
ax_radio_floor = plt.axes([0.65, 0.35, 0.25, 0.15])
ax_radio_walls = plt.axes([0.65, 0.18, 0.25, 0.15])
ax_radio_ceil = plt.axes([0.65, 0.01, 0.25, 0.15])

l_slider = Slider(ax=ax_sliders_l, label='Length (m)', valmin=1, valmax=30, valinit=initial_dims['l'])
w_slider = Slider(ax=ax_sliders_w, label='Width (m)', valmin=1, valmax=30, valinit=initial_dims['w'])
h_slider = Slider(ax=ax_sliders_h, label='Height (m)', valmin=2, valmax=10, valinit=initial_dims['h'])

#buttons
size_radio = RadioButtons(ax=ax_radio_size, labels=list(ROOM_SIZES.keys()), active=1)
floor_radio = RadioButtons(ax=ax_radio_floor, labels=MATERIALS, active=MATERIALS.index(initial_config['floor']))
walls_radio = RadioButtons(ax=ax_radio_walls, labels=MATERIALS, active=MATERIALS.index(initial_config['walls']))
ceil_radio = RadioButtons(ax=ax_radio_ceil, labels=MATERIALS, active=MATERIALS.index(initial_config['ceiling']))

#materials
ax_radio_size.set_title('Room Size Preset', y=0.9)
ax_radio_floor.set_title('Floor Material', y=0.9)
ax_radio_walls.set_title('Walls Material', y=0.9)
ax_radio_ceil.set_title('Ceiling Material', y=0.9)

def update(val):
    l = l_slider.val
    w = w_slider.val
    h = h_slider.val
    
    config = {
        'floor': floor_radio.value_selected,
        'walls': walls_radio.value_selected,
        'ceiling': ceil_radio.value_selected
    }
    
    new_rt60 = calculate_rt60(l, w, h, config)
    line.set_ydata(new_rt60)
    
    # Auto-adjust y-axis
    ax.set_ylim(0, max(2, np.max(new_rt60) * 1.2))
    
    fig.canvas.draw_idle()

def update_sliders_from_preset(label):
    dims = ROOM_SIZES[label]
    l_slider.set_val(dims['l'])
    w_slider.set_val(dims['w'])
    h_slider.set_val(dims['h'])
    
#connect to functions
l_slider.on_changed(update)
w_slider.on_changed(update)
h_slider.on_changed(update)
floor_radio.on_clicked(update)
walls_radio.on_clicked(update)
ceil_radio.on_clicked(update)
size_radio.on_clicked(update_sliders_from_preset)

plt.show()