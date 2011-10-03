#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .. import spin_box
from enaml.toolkit import qt_toolkit


class TestQtSpinBox(spin_box.TestSpinBox):
    """ QtSpinBox tests. """

    toolkit = qt_toolkit()

    def get_value(self, widget):
        """ Get a spin box's value.
        
        """
        return widget.value()

    def get_low(self, widget):
        """ Get a spin box's minimum value.
        
        """
        return widget.minimum()
    
    def get_high(self, widget):
        """ Get a spin box's maximum value.
        
        """
        return widget.maximum()

    def get_step(self, widget):
        """ Get a spin box's step size.
        
        """
        return widget.singleStep()
    
    def get_wrap(self, widget):
        """ Check if a spin box wraps around at the edge values.
        
        """
        return widget.wrapping()

    def get_prefix(self, widget):
        """ Get a spin box's text prefix.
        
        """
        return widget.prefix()
    
    def get_suffix(self, widget):
        """ Get a spin box's text suffix.
        
        """
        return widget.suffix()

    def get_special_value_text(self, widget):
        """ Get a spin box's special value text, displayed at the minimum value.
        
        """
        return widget.specialValueText()

    def get_to_string(self, widget):
        """ Get a spin box's value-to-display callable.
        
        """
        return widget.to_string
    
    def get_from_string(self, widget):
        """ Get a spin box's display-to-value callable.
        
        """
        return widget.from_string

    def get_text(self, widget):
        """ Get the text displayed in a spin box.
        
        """
        return widget.text()
    
    def spin_up_event(self, widget):
        """ Simulate a click on the 'up' spin button.
        
        """
        widget.stepUp()

    def spin_down_event(self, widget):
        """ Simulate a click on the 'down' spin button.
        
        """
        widget.stepDown()
