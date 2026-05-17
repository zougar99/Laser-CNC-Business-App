"""
CAD Canvas for drawing - AutoCAD-like interface
"""

import wx
import logging
from typing import List, Tuple, Optional
import numpy as np

logger = logging.getLogger(__name__)


class CADCanvas(wx.Panel):
    """
    CAD Canvas for drawing and editing.
    
    Features:
    - Drawing tools (line, circle, rectangle, etc.)
    - Zoom and pan
    - Selection
    - Grid display
    - Snap to grid
    """

    def __init__(self, parent, kernel=None):
        """
        Initialize the CAD canvas.
        
        Args:
            parent: Parent window
            kernel: Application kernel
        """
        super().__init__(parent, style=wx.BORDER_SUNKEN)
        
        self.kernel = kernel
        self.elements = []  # List of drawn elements
        self.selected_elements = []
        self.current_tool = None
        self.drawing_mode = False
        self.temp_points = []
        
        # View settings
        self.zoom = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.show_grid = True
        self.snap_to_grid = True
        self.grid_size = 10.0
        
        # Mouse state
        self.mouse_pos = (0, 0)
        self.drag_start = None
        self.is_dragging = False
        
        # Set background color
        self.SetBackgroundColour(wx.Colour(240, 240, 240))
        
        # Bind events
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_SIZE, self._on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self._on_mouse)
        self.Bind(wx.EVT_KEY_DOWN, self._on_key_down)
        self.Bind(wx.EVT_MOUSEWHEEL, self._on_mousewheel)
        
        logger.info("CAD Canvas created")

    def _on_paint(self, event):
        """Handle paint event."""
        dc = wx.PaintDC(self)
        self._draw(dc)

    def _draw(self, dc):
        """Draw the canvas content."""
        # Get canvas size
        width, height = self.GetClientSize()
        
        # Set up coordinate system
        dc.SetUserScale(self.zoom, self.zoom)
        dc.SetDeviceOrigin(int(self.pan_x), int(self.pan_y))
        
        # Draw background
        dc.SetBackground(wx.Brush(wx.Colour(255, 255, 255)))
        dc.Clear()
        
        # Draw grid
        if self.show_grid:
            self._draw_grid(dc, width, height)
        
        # Draw elements
        for element in self.elements:
            self._draw_element(dc, element)
        
        # Draw selection
        for element in self.selected_elements:
            self._draw_selection(dc, element)
        
        # Draw temporary points (during drawing)
        if self.drawing_mode and len(self.temp_points) > 0:
            self._draw_temp_points(dc)
        
        # Draw crosshair at mouse position
        self._draw_crosshair(dc)

    def _draw_grid(self, dc, width, height):
        """Draw the grid."""
        dc.SetPen(wx.Pen(wx.Colour(200, 200, 200), 1))
        
        # Calculate visible grid range
        start_x = int((self.pan_x / self.zoom) // self.grid_size) * self.grid_size
        start_y = int((self.pan_y / self.zoom) // self.grid_size) * self.grid_size
        end_x = start_x + (width / self.zoom) + self.grid_size
        end_y = start_y + (height / self.zoom) + self.grid_size
        
        # Draw vertical lines
        x = start_x
        while x <= end_x:
            dc.DrawLine(int(x), int(start_y), int(x), int(end_y))
            x += self.grid_size
        
        # Draw horizontal lines
        y = start_y
        while y <= end_y:
            dc.DrawLine(int(start_x), int(y), int(end_x), int(y))
            y += self.grid_size

    def _draw_element(self, dc, element):
        """Draw an element."""
        element_type = element.get('type', 'line')
        
        if element_type == 'line':
            dc.SetPen(wx.Pen(wx.Colour(0, 0, 0), 2))
            start = element.get('start', (0, 0))
            end = element.get('end', (0, 0))
            dc.DrawLine(int(start[0]), int(start[1]), int(end[0]), int(end[1]))
        
        elif element_type == 'circle':
            dc.SetPen(wx.Pen(wx.Colour(0, 0, 0), 2))
            center = element.get('center', (0, 0))
            radius = element.get('radius', 10)
            dc.DrawCircle(int(center[0]), int(center[1]), int(radius))
        
        elif element_type == 'rectangle':
            dc.SetPen(wx.Pen(wx.Colour(0, 0, 0), 2))
            pos = element.get('position', (0, 0))
            size = element.get('size', (100, 100))
            dc.DrawRectangle(int(pos[0]), int(pos[1]), int(size[0]), int(size[1]))

    def _draw_selection(self, dc, element):
        """Draw selection handles."""
        dc.SetPen(wx.Pen(wx.Colour(0, 100, 255), 2))
        dc.SetBrush(wx.Brush(wx.Colour(200, 220, 255), wx.BRUSHSTYLE_SOLID))
        
        # Draw selection box around element
        element_type = element.get('type', 'line')
        if element_type == 'line':
            start = element.get('start', (0, 0))
            end = element.get('end', (0, 0))
            # Draw handles at start and end
            self._draw_handle(dc, start)
            self._draw_handle(dc, end)

    def _draw_handle(self, dc, point, size=5):
        """Draw a selection handle."""
        x, y = int(point[0]), int(point[1])
        dc.DrawRectangle(x - size, y - size, size * 2, size * 2)

    def _draw_temp_points(self, dc):
        """Draw temporary points during drawing."""
        dc.SetPen(wx.Pen(wx.Colour(255, 0, 0), 2))
        for point in self.temp_points:
            self._draw_handle(dc, point, 3)

    def _draw_crosshair(self, dc):
        """Draw crosshair at mouse position."""
        if self.mouse_pos:
            x, y = self._screen_to_world(self.mouse_pos[0], self.mouse_pos[1])
            dc.SetPen(wx.Pen(wx.Colour(100, 100, 100), 1, wx.PENSTYLE_DOT))
            size = 20
            dc.DrawLine(int(x - size), int(y), int(x + size), int(y))
            dc.DrawLine(int(x), int(y - size), int(x), int(y + size))

    def _on_size(self, event):
        """Handle size event."""
        self.Refresh()

    def _on_mouse(self, event):
        """Handle mouse events."""
        self.mouse_pos = event.GetPosition()
        world_pos = self._screen_to_world(self.mouse_pos[0], self.mouse_pos[1])
        
        # Snap to grid if enabled
        if self.snap_to_grid:
            world_pos = self._snap_to_grid(world_pos)
        
        # Update status bar
        if hasattr(self.GetParent().GetParent(), 'statusbar'):
            self.GetParent().GetParent().statusbar.SetStatusText(
                "X: {:.2f}".format(world_pos[0]), 1
            )
            self.GetParent().GetParent().statusbar.SetStatusText(
                "Y: {:.2f}".format(world_pos[1]), 2
            )
        
        if event.LeftDown():
            self._on_left_down(world_pos)
        elif event.LeftUp():
            self._on_left_up(world_pos)
        elif event.RightDown():
            self._on_right_down(world_pos)
        elif event.Moving():
            self._on_mouse_move(world_pos)
        
        self.Refresh()

    def _on_left_down(self, pos):
        """Handle left mouse button down."""
        if self.current_tool == 'line':
            if len(self.temp_points) == 0:
                self.temp_points = [pos]
                self.drawing_mode = True
            elif len(self.temp_points) == 1:
                # Complete line
                self.elements.append({
                    'type': 'line',
                    'start': self.temp_points[0],
                    'end': pos
                })
                self.temp_points = []
                self.drawing_mode = False
        elif self.current_tool == 'circle':
            if len(self.temp_points) == 0:
                self.temp_points = [pos]
                self.drawing_mode = True
            elif len(self.temp_points) == 1:
                # Complete circle
                center = self.temp_points[0]
                radius = np.sqrt((pos[0] - center[0])**2 + (pos[1] - center[1])**2)
                self.elements.append({
                    'type': 'circle',
                    'center': center,
                    'radius': radius
                })
                self.temp_points = []
                self.drawing_mode = False
        else:
            # Selection mode
            self._select_at_position(pos)

    def _on_left_up(self, pos):
        """Handle left mouse button up."""
        pass

    def _on_right_down(self, pos):
        """Handle right mouse button down."""
        # Cancel current drawing
        if self.drawing_mode:
            self.temp_points = []
            self.drawing_mode = False
            self.Refresh()

    def _on_mouse_move(self, pos):
        """Handle mouse move."""
        if self.drawing_mode and len(self.temp_points) > 0:
            self.Refresh()

    def _on_key_down(self, event):
        """Handle key down event."""
        key = event.GetKeyCode()
        
        if key == wx.WXK_DELETE:
            # Delete selected elements
            for element in self.selected_elements:
                if element in self.elements:
                    self.elements.remove(element)
            self.selected_elements = []
            self.Refresh()
        elif key == wx.WXK_ESCAPE:
            # Cancel drawing
            if self.drawing_mode:
                self.temp_points = []
                self.drawing_mode = False
                self.Refresh()
        
        event.Skip()

    def _on_mousewheel(self, event):
        """Handle mouse wheel for zooming."""
        rotation = event.GetWheelRotation()
        if rotation > 0:
            self.zoom *= 1.1
        else:
            self.zoom /= 1.1
        
        # Limit zoom
        self.zoom = max(0.1, min(10.0, self.zoom))
        self.Refresh()

    def _screen_to_world(self, x, y):
        """Convert screen coordinates to world coordinates."""
        world_x = (x - self.pan_x) / self.zoom
        world_y = (y - self.pan_y) / self.zoom
        return (world_x, world_y)

    def _snap_to_grid(self, pos):
        """Snap position to grid."""
        x = round(pos[0] / self.grid_size) * self.grid_size
        y = round(pos[1] / self.grid_size) * self.grid_size
        return (x, y)

    def _select_at_position(self, pos):
        """Select element at position."""
        # Simple selection - find closest element
        self.selected_elements = []
        min_dist = float('inf')
        closest = None
        
        for element in self.elements:
            dist = self._distance_to_element(pos, element)
            if dist < min_dist and dist < 10:  # 10 pixel threshold
                min_dist = dist
                closest = element
        
        if closest:
            self.selected_elements = [closest]
        self.Refresh()

    def _distance_to_element(self, pos, element):
        """Calculate distance from point to element."""
        element_type = element.get('type', 'line')
        if element_type == 'line':
            start = element.get('start', (0, 0))
            end = element.get('end', (0, 0))
            # Distance to line segment
            return self._point_to_line_distance(pos, start, end)
        elif element_type == 'circle':
            center = element.get('center', (0, 0))
            radius = element.get('radius', 10)
            dist = np.sqrt((pos[0] - center[0])**2 + (pos[1] - center[1])**2)
            return abs(dist - radius)
        return float('inf')

    def _point_to_line_distance(self, point, line_start, line_end):
        """Calculate distance from point to line segment."""
        # Simplified distance calculation
        x0, y0 = point
        x1, y1 = line_start
        x2, y2 = line_end
        
        A = x0 - x1
        B = y0 - y1
        C = x2 - x1
        D = y2 - y1
        
        dot = A * C + B * D
        len_sq = C * C + D * D
        
        if len_sq == 0:
            return np.sqrt(A * A + B * B)
        
        param = dot / len_sq
        
        if param < 0:
            xx, yy = x1, y1
        elif param > 1:
            xx, yy = x2, y2
        else:
            xx, yy = x1 + param * C, y1 + param * D
        
        dx = x0 - xx
        dy = y0 - yy
        return np.sqrt(dx * dx + dy * dy)

    def set_tool(self, tool_name):
        """Set the current drawing tool."""
        self.current_tool = tool_name
        self.temp_points = []
        self.drawing_mode = False
        logger.info("Tool set to: {}".format(tool_name))

    def new_document(self):
        """Create a new document."""
        self.elements = []
        self.selected_elements = []
        self.temp_points = []
        self.drawing_mode = False
        self.Refresh()

    def load_file(self, filename):
        """Load file (placeholder)."""
        logger.info("Loading file: {}".format(filename))
        # TODO: Implement file loading

    def save_file(self, filename):
        """Save file (placeholder)."""
        logger.info("Saving file: {}".format(filename))
        # TODO: Implement file saving

    def cleanup(self):
        """Cleanup resources."""
        pass
