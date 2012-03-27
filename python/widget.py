#!/usr/bin/python

import gobject
import pygtk
pygtk.require("2.0")
import gtk
from gtk import gdk

if gtk.pygtk_version < (2, 8):
    print "PyGtk 2.8 or later required for this example"
    raise SystemExit

#import sys

DEFAULT_XPADSZ = 70
DEFAULT_FONT_NAME = "-misc-fixed-medium-r-normal--10-70-100-100-c-60-iso8859-1"

NOTE_MAX = 127

MIDI_NOTEOFF_EVENT = 0x8
MIDI_NOTEON_EVENT  = 0x9

DEFAULT_NOTEON_VAL = 100

DEFAULT_YPADSZ = gdk.Font(DEFAULT_FONT_NAME).string_height("C -10X") + 4

class ProgressLineWidget(object):
    def draw_progressline(self, area):
        if self.line_xpos >= area.x and self.line_xpos <= (area.x, + area.width):
            ymin = area.y
            ymax = area.y + area.height
            self.window.draw_line(self.style.fg_gc[gtk.STATE_NORMAL],
                                  self.line_xpos, ymin, self.line_xpos, ymax)

    def clear_progressline(self):
        lwidth, lheight = self.line_cache.get_size()
        self.window.draw_drawable(self.style.fg_gc[gtk.STATE_NORMAL],
                                  self.line_cache, 0, 0, self.line_xpos, 0, 1, lheight)

    def _update_pos(self, pos):
        width, height = self.window.get_size()
        if self.line_cache == None:
            self.line_cache = gtk.gdk.Pixmap(self.window, 1, height)
        else:
            lwidth, lheight = self.line_cache.get_size()
            self.window.draw_drawable(self.style.fg_gc[gtk.STATE_NORMAL],
                                      self.line_cache, 0, 0, self.line_xpos, 0, 1, lheight)
            if lheight != height:
                self.line_cache = gtk.gdk.Pixmap(self.window, 1, height)

        self.line_cache.draw_drawable(self.style.fg_gc[gtk.STATE_NORMAL],
                                      self.window, pos, 0, 0, 0, 1, height)
        self.window.draw_line(self.style.fg_gc[gtk.STATE_NORMAL],
                              pos, 0, pos, height)
        self.line_xpos = pos


class MsqHBarTimeWidget(gtk.Widget):
    def __init__(self, track_len, mlen=4, xpadsz=DEFAULT_XPADSZ, font_name=DEFAULT_FONT_NAME):
        gtk.Widget.__init__(self)

        self.mlen = mlen
        self.xpadsz = xpadsz
        self.hbarlen = xpadsz * track_len

        self.font = gdk.Font(font_name)
        self.font_height = self.font.string_height("3600")
        self.height = (self.font_height + 1) * 3

    def do_realize(self):
        self.set_flags(gtk.REALIZED)
        self.window = gdk.Window(self.get_parent_window(),
                                 width=self.allocation.width,
                                 height=self.allocation.height,
                                 window_type=gdk.WINDOW_CHILD,
                                 wclass=gdk.INPUT_OUTPUT,
                                 event_mask=self.get_events() | gdk.EXPOSURE_MASK)
        self.window.set_user_data(self)
        self.window.move_resize(*self.allocation)

        self.dark_gc = self.style.dark_gc[gtk.STATE_NORMAL]
        self.fg_gc = self.style.fg_gc[gtk.STATE_NORMAL]

        # self.dark = self.window.new_gc()

        # self.light = self.window.new_gc()
        # self.light.set_foreground(self.style.dark_gc[gtk.STATE_NORMAL].foreground)

        # self.bg_gc = self.window.new_gc()
        # self.bg_gc.set_foreground(self.style.bg_gc[gtk.STATE_NORMAL].foreground)

    def do_unrealize(self):
        self.window.set_user_data(None)

    def do_size_request(self, requisition):
        requisition.width  = self.hbarlen
        requisition.height = self.height

    def do_size_allocate(self, allocation):
        self.allocation = allocation
        if self.flags() & gtk.REALIZED:
            self.window.move_resize(*self.allocation)

    def do_expose_event(self, event):
        area = event.area
        self.window.draw_rectangle(self.dark_gc,
                                   True,
                                   area.x,
                                   area.y,
                                   area.width,
                                   area.height)
        xmax = area.x + area.width
        ymax = area.y + area.height
        # if ymax > self.max_height:
        #     ymax = self.max_height
        xpos = area.x - (area.x % self.xpadsz)
        time_pos = xpos / self.xpadsz

        mypos = self.font_height * 2
        nypos = self.font_height * 5 / 2
        while xpos <= xmax:
            if (time_pos % self.mlen) == 0:
                self.window.draw_string(self.font, self.fg_gc, xpos, 2 + self.font_height, "%i" % time_pos)
                ypos = mypos
            else:
                ypos = nypos
            if area.y > ypos:
                ypos = area.y
            self.window.draw_line(self.fg_gc, xpos, ypos, xpos, ymax)
            time_pos += 1
            xpos += self.xpadsz
        ypos = self.height - 1
        self.window.draw_line(self.fg_gc, area.x, ypos, area.x + area.width, ypos)

class MsqVBarNoteWidget(gtk.Widget):
    def __init__(self, font_name=DEFAULT_FONT_NAME):
        gtk.Widget.__init__(self)

        self.font = gdk.Font(font_name)
        self.font_height = self.font.string_height("C -10X")
        self.width = self.font.string_width("C -10X")

        self.ypadsz = self.font_height + 4
        self.max_height = (NOTE_MAX + 1) * self.ypadsz + 1

    def do_realize(self):
        self.set_flags(gtk.REALIZED)
        self.window = gdk.Window(self.get_parent_window(),
                                 width=self.allocation.width,
                                 height=self.allocation.height,
                                 window_type=gdk.WINDOW_CHILD,
                                 wclass=gdk.INPUT_OUTPUT,
                                 event_mask=self.get_events() | gdk.EXPOSURE_MASK)
        self.window.set_user_data(self)
        self.window.move_resize(*self.allocation)

        self.dark = self.window.new_gc()

        self.bg_gc = self.window.new_gc()
        self.bg_gc.set_foreground(self.style.bg_gc[gtk.STATE_NORMAL].foreground)

    def do_unrealize(self):
        self.window.set_user_data(None)

    def do_size_request(self, requisition):
        requisition.width  = self.width
        requisition.height = self.max_height

    def do_size_allocate(self, allocation):
        self.allocation = allocation
        if self.flags() & gtk.REALIZED:
            self.window.move_resize(*self.allocation)

    def do_expose_event(self, event):
        area = event.area
        xmax = area.x + area.width
        ymax = area.y + area.height
        ypos = area.y - (area.y % self.ypadsz)
        note_pos = ypos / self.ypadsz
        octave = ((128 - note_pos) / 12) - 2

        self.window.draw_rectangle(self.bg_gc,
                                   True,
                                   area.x,
                                   area.y,
                                   area.width,
                                   area.height)

        win_xsize , win_ysize = self.window.get_size()
        if (xmax >= win_xsize):
            self.window.draw_line(self.dark, win_xsize - 1, area.y, win_xsize - 1, ymax)

        while ypos < ymax:
            self.window.draw_line(self.dark, area.x, ypos, xmax, ypos)
            note_pos += 1
            ypos += self.ypadsz
            if ((128 - note_pos) % 12) == 0:
                self.window.draw_string(self.font, self.dark, 3, ypos - 1, "C %i" % octave)
                octave -= 1


NOTE_PX_SIZE = 8

note_off_xpm = ["%i %i 2 1" % (NOTE_PX_SIZE, NOTE_PX_SIZE),
                "  c None",
                "x c #000000",
                "        ",
                "        ",
                "  xxxx  ",
                "  x  x  ",
                "  x  x  ",
                "  xxxx  ",
                "        ",
                "        "]

note_on_xpm = ["%i %i 2 1" % (NOTE_PX_SIZE, NOTE_PX_SIZE),
               "  c None",
               "x c #000000",
               "        ",
               " xxxxxx ",
               " xx  xx ",
               " x xx x ",
               " x xx x ",
               " xx  xx ",
               " xxxxxx ",
               "        "]

NOTE_BAR_TYPE = 0
NOTE_POINT_TYPE = 1

class MsqNoteGridWidget(gtk.Widget, ProgressLineWidget):
    def set_pad_size(self, xpadsz, ypadsz):
        self.xpadsz = xpadsz
        self.ypadsz = ypadsz
        self.max_height = (NOTE_MAX + 1) * self.ypadsz + 1

    def update_pos(self, tickpos):
        xpos = int(tickpos * self.xpadsz / self.ppq)
        self._update_pos(xpos)

    def __init__(self, chan_num, track_len, track, mlen=4, ppq=48, xpadsz=DEFAULT_XPADSZ, ypadsz=DEFAULT_YPADSZ, note_type=NOTE_BAR_TYPE):
        gtk.Widget.__init__(self)
        self.chan_num = chan_num
        self.mlen = mlen # 4/4 or 3/4
        self.ppq = ppq
        self.set_pad_size(xpadsz, ypadsz)
        # self.track_events = track_events
        self.track_len = track_len
        self.track = track
        self.note_param = {"channel": 0, "val_on": DEFAULT_NOTEON_VAL, "val_off": 0, "len": ppq / 4, "quant": ppq / 4}
        self.note_type = note_type
        self.button3down = False
        self.line_cache = None
        self.selection = ([], [])

    def refresh_note(self, tick, note, len, val_on, val_off=0):
        xpos = tick * self.xpadsz / self.ppq
        xsize = len * self.xpadsz / self.ppq
        ypos = ((127 - note) * self.ypadsz) + 1
        if xpos > (NOTE_PX_SIZE / 2):
            xpos = xpos - (NOTE_PX_SIZE / 2)
        else:
            xpos = 0
        if ypos > (NOTE_PX_SIZE / 2):
            ypos = ypos - (NOTE_PX_SIZE / 2)
        else:
            ypos = 0
        self.draw_all(gtk.gdk.Rectangle(xpos, ypos, xsize + NOTE_PX_SIZE, self.ypadsz + NOTE_PX_SIZE))

    def xpos2tick(self, xpos):
        return int(xpos * self.ppq / self.xpadsz)

    def ypos2noteval(self, ypos):
        return int(128 - (ypos / self.ypadsz))

    def add_note(self, xpos, ypos):
        tick = self.xpos2tick(xpos)
        tick = int(tick / self.note_param["quant"]) * self.note_param["quant"]
        note = self.ypos2noteval(ypos)

        self.track.add_note_event(tick,
                                  MIDI_NOTEON_EVENT,
                                  self.note_param["channel"],
                                  note,
                                  self.note_param["val_on"])
        self.track.add_note_event(tick + self.note_param["len"],
                                  MIDI_NOTEOFF_EVENT,
                                  self.note_param["channel"],
                                  note,
                                  self.note_param["val_off"])

        self.refresh_note(tick,
                          note,
                          self.note_param["len"],
                          self.note_param["val_on"],
                          self.note_param["val_off"])

    def handle_button_release(self, widget, event):
        if event.button == 3:
            self.window.set_cursor(self.cursor_arrow)
            self.button3down = False
        if event.button == 1:
            if self.button3down:
                self.add_note(event.x, event.y)
            else:
                self.selection = self.select_note(event.x, event.y)
                # print self.selection

    def select_note(self, xpos, ypos):
        evwr = self.track.get_evwr()
        if not evwr:
            return []

        tick = self.xpos2tick(xpos)
        noteval = self.ypos2noteval(ypos)
        selection = []
        noteon = []
        noteon_tmp_len = 0
        noteoff = []

        event = evwr.get_event()
        while event:
            ev_channel = event[2]
            if ev_channel != self.chan_num:
                event = evwr.goto_next()
                continue
            ev_tick = event[0]
            ev_type = event[1]
            ev_note = event[3]
            if ev_tick <= tick:
                if ev_type == MIDI_NOTEON_EVENT and ev_note == noteval:
                    noteon.append(evwr.copy())
                    event = evwr.goto_next()
                    continue
                if ev_type == MIDI_NOTEOFF_EVENT and ev_note == noteval:
                    if len(noteon) > 0:
                        noteon.pop(0)
            else:
                if ev_type == MIDI_NOTEOFF_EVENT and ev_note == noteval:
                    noteoff.append(evwr.copy())
                    event = evwr.goto_next()
                    continue
                if ev_type == MIDI_NOTEON_EVENT and ev_note == noteval:
                    noteon_tmp_len += 1
            event = evwr.goto_next()
        while noteon_tmp_len > 0 and len(noteoff) > 0:
            noteoff.pop()
            noteon_tmp_len -= 1
        selection.extend(noteon)
        selection.extend(noteoff)
        selection.sort(cmp=lambda x, y: x.get_event()[0] > y.get_event()[0])
        return selection

    def handle_button_press(self, widget, event):
        self.grab_focus()
        if event.button == 3:
            self.window.set_cursor(self.cursor_pencil)
            self.button3down = True

    def handle_key_press(self, widget, event):
        self.grab_focus()
        # print event.keyval, gtk.DELETE
        # print gtk.gdk.keyval_name(event.keyval)
        # print event.string
        if event.keyval == gtk.keysyms.Delete or event.keyval == gtk.keysyms.BackSpace:
            for evwr in self.selection:
                evwr.del_event()
            self.selection = []

    def do_realize(self):
        self.set_flags(gtk.REALIZED)
        self.window = gdk.Window(self.get_parent_window(),
                                 width=self.allocation.width,
                                 height=self.allocation.height,
                                 window_type=gdk.WINDOW_CHILD,
                                 wclass=gdk.INPUT_OUTPUT,
                                 event_mask=self.get_events() | gdk.EXPOSURE_MASK | gdk.BUTTON_PRESS_MASK | gdk.BUTTON_RELEASE_MASK | gdk.KEY_PRESS_MASK)
        self.window.set_user_data(self)
        self.window.move_resize(*self.allocation)

        self.grid_fg = self.style.fg[gtk.STATE_ACTIVE]
        self.grid_bg = self.style.bg[gtk.STATE_ACTIVE]
        self.grid_light = gtk.gdk.Color((self.grid_fg.red + self.grid_bg.red) / 2,
                                        (self.grid_fg.green + self.grid_bg.green) / 2,
                                        (self.grid_fg.blue + self.grid_bg.blue) / 2)

        self.dark = self.window.new_gc()

        self.bg_gc = self.window.new_gc()
        self.bg_gc.set_foreground(self.style.bg_gc[gtk.STATE_NORMAL].foreground)

        self.light = self.window.new_gc()
        self.light.set_foreground(self.style.dark_gc[gtk.STATE_NORMAL].foreground)

        self.cross_pxb = gtk.gdk.pixbuf_new_from_xpm_data(note_on_xpm)
        self.square_pxb = gtk.gdk.pixbuf_new_from_xpm_data(note_off_xpm)

        self.connect("button_press_event", self.handle_button_press)
        self.connect("button_release_event", self.handle_button_release)
        self.connect("key_press_event", self.handle_key_press)
        self.cursor_arrow = gtk.gdk.Cursor(gtk.gdk.LEFT_PTR)
        self.cursor_pencil = gtk.gdk.Cursor(gtk.gdk.PENCIL)
        self.window.set_cursor(self.cursor_arrow)
        self.set_can_focus(True)


    def do_unrealize(self):
        self.window.set_user_data(None)

    def do_size_request(self, requisition):
        requisition.width  = self.xpadsz * self.track_len
        requisition.height = self.max_height

    def do_size_allocate(self, allocation):
        self.allocation = allocation
        if self.flags() & gtk.REALIZED:
            self.window.move_resize(*self.allocation)

    def draw_grid(self, area):
        xmax = area.x + area.width
        ymax = area.y + area.height
        if ymax > self.max_height:
            ymax = self.max_height
        xpos = area.x - (area.x % self.xpadsz)
        ypos = area.y - (area.y % self.ypadsz)
        time_pos = xpos / self.xpadsz
        note_pos = ypos / self.ypadsz

        cr = self.window.cairo_create()
        cr.set_source_color(self.grid_bg)
        cr.rectangle(area.x, area.y, area.width, area.height)
        cr.fill()

        cr.set_line_width(1)
        # dx = 0.5
        # dy = dx
        # cr.device_to_user_distance(dx, dy)
        # cr.set_line_width(dx if dx > dy else dy)
        # import pdb; pdb.set_trace()
        while xpos <= xmax:
            if  (time_pos % self.mlen) == 0:
                cr.set_source_color(self.grid_fg)
            else:
                cr.set_source_color(self.grid_light)
            cr.move_to(xpos + 0.5, area.y + 0.5)
            cr.line_to(xpos + 0.5, ymax + 0.5)
            cr.stroke()
            time_pos += 1
            xpos += self.xpadsz

        while ypos < ymax:
            if ((128 - note_pos) % 12) == 0:
                cr.set_source_color(self.grid_fg)
            else:
                cr.set_source_color(self.grid_light)
            cr.move_to(area.x + 0.5, ypos + 0.5)
            cr.line_to(xmax + 0.5, ypos + 0.5)
            cr.stroke()
            # gc = self.dark if ((128 - note_pos) % 12) == 0 else self.light
            # self.window.draw_line(gc, area.x, ypos, xmax, ypos)
            note_pos += 1
            ypos += self.ypadsz

    def draw_notes_bar(self, area):
        xmax = area.x + area.width
        ymax = area.y + area.height
        if ymax > self.max_height: # Handling max notes height
            ymax = self.max_height

        def pop_1st_note_in_list(note, noteon_list):
            for noteon in noteon_list:
                if noteon[0] == note:
                    noteon_list.remove(noteon)
                    return noteon

        noteon_list = []
        noteon_bkp = []
        evwr = self.track.get_evwr()
        if evwr:
            event = evwr.get_event()
        else:
            event = None
        while event:
            ev_type = event[1]
            ev_chan = event[2]
            if ev_chan != self.chan_num or not ev_type in (MIDI_NOTEOFF_EVENT, MIDI_NOTEON_EVENT):
                event = evwr.goto_next()
                continue
            tick = event[0]
            ev_note = event[3]
            xpos = tick * self.xpadsz / self.ppq
            # Handling possible couple of 'note on' and 'note off' around area position
            if xpos < area.x:
                if ev_type == MIDI_NOTEON_EVENT:
                    noteon_bkp.append((ev_note, xpos))
                elif ev_type == MIDI_NOTEOFF_EVENT:
                    pop_1st_note_in_list(ev_note, noteon_bkp)
                event = evwr.goto_next()
                continue
            if xpos > xmax:
                if ev_type == MIDI_NOTEOFF_EVENT:
                    noteon = pop_1st_note_in_list(ev_note, noteon_bkp)
                    if noteon:
                        ypos = ((127 - ev_note) * self.ypadsz)
                        ysize = self.ypadsz - 1
                        if ypos > ymax or (ypos + ysize) < area.y:
                            continue
                        if (ypos + ysize) > ymax:
                            ysize = ymax - ypos
                        self.window.draw_rectangle(self.light, True, area.x, ypos + 1, area.width, ysize)
                event = evwr.goto_next()
                continue

            # Handling note on area position
            ypos = ((127 - ev_note) * self.ypadsz)
            ysize = self.ypadsz - 1
            if ypos > ymax:
                event = evwr.goto_next()
                continue
            if (ypos + ysize) < area.y:
                event = evwr.goto_next()
                continue
            if (ypos + ysize) > ymax:
                ysize = ymax - ypos

            if ysize > 0:
                if ev_type == MIDI_NOTEON_EVENT:
                    noteon_list.append((ev_note, xpos, ypos + 1, ysize))
                else: # MIDI_NOTEOFF_EVENT
                    noteon = pop_1st_note_in_list(ev_note, noteon_list)
                    if noteon == None:
                        noteon = pop_1st_note_in_list(ev_note, noteon_bkp)
                    if noteon == None:
                        # Handling noteoff with no preceding noteon
                        xsize = xpos - area.x
                        if xsize > 0:
                            self.window.draw_rectangle(self.light, True, area.x, ypos + 1, xsize, ysize)
                    else:
                        xsize = xpos - noteon[1]
                        self.window.draw_rectangle(self.light, True, noteon[1], ypos + 1, xsize, ysize)
            event = evwr.goto_next()
            continue

        # Handling noteon with no noteoff (to resolve some scroll problem)
        for noteon in noteon_list:
            xsize = area.x + area.width - noteon[1]
            self.window.draw_rectangle(self.light, True, noteon[1], noteon[2], xsize, noteon[3])

    def draw_notes_points(self, area):
        xmax = area.x + area.width
        ymax = area.y + area.height
        if ymax > self.max_height: # Handling max notes height
            ymax = self.max_height
        evwr = self.track.get_evwr()
        if evwr:
            event = evwr.get_event()
            while event != None:
                ev_channel = event[2]
                if ev_channel != self.chan_num:
                    event = evwr.goto_next()
                    continue
                ev_tick = event[0]
                xpos = ev_tick * self.xpadsz / self.ppq
                if xpos < area.x:
                    event = evwr.goto_next()
                    continue
                if xpos > xmax:
                    event = evwr.goto_next()
                    continue
                ev_type = event[1]
                # Handling note on area position
                if not (ev_type == MIDI_NOTEOFF_EVENT or ev_type == MIDI_NOTEON_EVENT):
                    event = evwr.goto_next()
                    continue
                ev_note = event[3]
                ypos = ((127 - ev_note) * self.ypadsz) + 1
                ysize = self.ypadsz - 1
                if ypos > ymax:
                    event = evwr.goto_next()
                    continue
                if (ypos + ysize) < area.y:
                    event = evwr.goto_next()
                    continue
                if ev_type == MIDI_NOTEON_EVENT:
                    self.window.draw_pixbuf(None, self.cross_pxb, 0, 0, xpos - (NOTE_PX_SIZE / 2), ypos + (ysize / 2) - (NOTE_PX_SIZE / 2))
                if ev_type == MIDI_NOTEOFF_EVENT:
                    self.window.draw_pixbuf(None, self.square_pxb, 0, 0, xpos - (NOTE_PX_SIZE / 2), ypos + (ysize / 2) - (NOTE_PX_SIZE / 2))
                event = evwr.goto_next()


    def draw_all(self, area):
        self.draw_grid(area)
        if self.note_type == NOTE_BAR_TYPE:
            self.draw_notes_bar(area)
        else:
            self.draw_notes_points(area)

    def set_draw_points_mode(self):
        self.note_type = NOTE_POINT_TYPE
    def set_draw_bars_mode(self):
        self.note_type = NOTE_BAR_TYPE

    def do_expose_event(self, event):
        self.draw_all(event.area)

gobject.type_register(MsqHBarTimeWidget)
gobject.type_register(MsqVBarNoteWidget)
gobject.type_register(MsqNoteGridWidget)
