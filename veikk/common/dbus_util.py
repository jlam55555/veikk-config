from pydbus import SystemBus
from pydbus.generic import signal
from gi.repository import GLib

bus = SystemBus()

remote_object = bus.get('org.freedesktop.DBus',
                        '/org/freedesktop/DBus')
print(remote_object.Introspect())


loop = GLib.MainLoop()


class Example:
    """
    Sample class from:
    https://github.com/LEW21/pydbus/blob/master/doc/tutorial.rst
    """

    # export introspection data
    dbus = """
    <node>
      <interface name='com.veikk.veikkd'>
        <method name='EchoString'>
          <arg type='s' name='a' direction='in'/>
          <arg type='s' name='response' direction='out'/>
        </method>
        <property name='SomeProperty' type='s' access='readwrite'>
          <annotation name='org.freedesktop.DBus.Property.EmitsChangedSignal'
                      value='true'/>
        </property>
      </interface>
    </node>
    """

    # export dbus signal
    PropertiesChanged = signal()

    def EchoString(self, s):
        return s

    def __init__(self):
        self._some_property = 'initial value'

    @property
    def SomeProperty(self):
        return self._some_property

    @SomeProperty.setter
    def SomeProperty(self, value):
        self._some_property = value
        self.PropertiesChanged('com.veikk.veikkd',
                               {'SomeProperty': self.SomeProperty}, [])

bus.publish('com.veikk.veikkd', Example())
loop.run()
