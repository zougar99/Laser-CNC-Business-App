"""
Layers Panel - AutoCAD-like interface
"""

import wx
import logging

logger = logging.getLogger(__name__)


class LayersPanel(wx.Panel):
    """
    Layers panel for managing drawing layers.
    """

    def __init__(self, parent, kernel=None):
        """
        Initialize the layers panel.
        
        Args:
            parent: Parent window
            kernel: Application kernel
        """
        super().__init__(parent, style=wx.BORDER_SUNKEN)
        
        self.kernel = kernel
        self.layers = [{"name": "Layer 0", "visible": True, "locked": False}]
        self.current_layer = 0
        
        self._create_ui()
        logger.info("Layers panel created")

    def _create_ui(self):
        """Create the UI."""
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Title
        title = wx.StaticText(self, label="Layers")
        title.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        sizer.Add(title, 0, wx.ALL, 5)
        
        # Layers list
        self.layers_list = wx.ListCtrl(
            self,
            style=wx.LC_REPORT | wx.LC_SINGLE_SEL
        )
        self.layers_list.InsertColumn(0, "Name", width=100)
        self.layers_list.InsertColumn(1, "Visible", width=60)
        self.layers_list.InsertColumn(2, "Locked", width=60)
        
        self._refresh_layers()
        
        sizer.Add(self.layers_list, 1, wx.EXPAND | wx.ALL, 5)
        
        # Buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        new_btn = wx.Button(self, label="New")
        new_btn.Bind(wx.EVT_BUTTON, self._on_new_layer)
        btn_sizer.Add(new_btn, 1, wx.EXPAND | wx.ALL, 2)
        
        delete_btn = wx.Button(self, label="Delete")
        delete_btn.Bind(wx.EVT_BUTTON, self._on_delete_layer)
        btn_sizer.Add(delete_btn, 1, wx.EXPAND | wx.ALL, 2)
        
        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        self.SetSizer(sizer)

    def _refresh_layers(self):
        """Refresh the layers list."""
        self.layers_list.DeleteAllItems()
        
        for i, layer in enumerate(self.layers):
            index = self.layers_list.InsertItem(self.layers_list.GetItemCount(), layer["name"])
            self.layers_list.SetItem(index, 1, "✓" if layer["visible"] else "")
            self.layers_list.SetItem(index, 2, "🔒" if layer["locked"] else "")

    def _on_new_layer(self, event):
        """Handle new layer button."""
        dialog = wx.TextEntryDialog(self, "Enter layer name:", "New Layer", "Layer {}".format(len(self.layers)))
        if dialog.ShowModal() == wx.ID_OK:
            name = dialog.GetValue()
            if name:
                self.layers.append({"name": name, "visible": True, "locked": False})
                self._refresh_layers()
                logger.info("New layer created: {}".format(name))
        dialog.Destroy()

    def _on_delete_layer(self, event):
        """Handle delete layer button."""
        selected = self.layers_list.GetFirstSelected()
        if selected >= 0 and len(self.layers) > 1:
            del self.layers[selected]
            self._refresh_layers()
            logger.info("Layer deleted")
