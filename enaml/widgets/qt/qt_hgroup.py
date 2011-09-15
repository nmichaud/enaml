from traits.api import implements

from .qt_group import QtGroup

from ..hgroup import IHGroupImpl


class QtHGroup(QtGroup):
    """ A Qt implementation of IHGroup.

    This is a convienence subclass of QtGroup which restricts the
    layout direction to horizontal.

    See Also
    --------
    IHGroup
    
    """ 
    implements(IHGroupImpl)

    #---------------------------------------------------------------------------
    # IHGroupImpl interface
    #---------------------------------------------------------------------------
    
    # IHGroupImpl interface is empty and fully implemented by QtGroup
    
    # XXX should we change implementation to use QHBoxLayout?

