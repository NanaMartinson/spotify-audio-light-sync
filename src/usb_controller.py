"""
USB controller module for controlling RGB USB lights.
"""

import usb.core
import usb.util
import time
from typing import Optional, Tuple


class USBController:
    """Controls USB RGB light devices."""
    
    def __init__(self, vendor_id: Optional[int] = None, 
                 product_id: Optional[int] = None,
                 simulate: bool = True):
        """
        Initialize USB controller.
        
        Args:
            vendor_id: USB vendor ID (hex, e.g., 0x1234)
            product_id: USB product ID (hex, e.g., 0x5678)
            simulate: Run in simulation mode (no actual USB device)
        """
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.simulate = simulate
        self.device = None
        self.last_update_time = 0
        self.min_update_interval = 1.0 / 60  # 60 Hz max update rate
        
    def connect(self) -> bool:
        """
        Connect to USB device.
        
        Returns:
            True if connected successfully, False otherwise
        """
        if self.simulate:
            print("Running in SIMULATE mode - no actual USB device control")
            return True
        
        if self.vendor_id is None or self.product_id is None:
            print("Error: vendor_id and product_id must be specified for USB mode")
            return False
        
        try:
            # Find the device
            self.device = usb.core.find(
                idVendor=self.vendor_id,
                idProduct=self.product_id
            )
            
            if self.device is None:
                print(f"USB device not found (VID: 0x{self.vendor_id:04x}, PID: 0x{self.product_id:04x})")
                return False
            
            # Set configuration
            try:
                self.device.set_configuration()
            except usb.core.USBError:
                # Device might already be configured
                pass
            
            print(f"Connected to USB device (VID: 0x{self.vendor_id:04x}, PID: 0x{self.product_id:04x})")
            return True
            
        except Exception as e:
            print(f"Error connecting to USB device: {e}")
            return False
    
    def set_color(self, r: int, g: int, b: int) -> bool:
        """
        Set RGB color of the light.
        
        Args:
            r, g, b: RGB values (0-255)
            
        Returns:
            True if color set successfully, False otherwise
        """
        # Rate limiting
        current_time = time.time()
        if current_time - self.last_update_time < self.min_update_interval:
            return True
        self.last_update_time = current_time
        
        if self.simulate:
            # Simulate mode - just return success
            return True
        
        if self.device is None:
            return False
        
        try:
            # Generic RGB USB light protocol
            # This is a common protocol, but may need adjustment for specific devices
            data = [0x00, r, g, b]
            self.device.write(0x01, data, 100)
            return True
            
        except Exception as e:
            print(f"Error setting USB color: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from USB device."""
        if self.device is not None:
            try:
                usb.util.dispose_resources(self.device)
            except Exception:
                pass
            self.device = None
    
    @staticmethod
    def list_usb_devices():
        """List all USB devices."""
        devices = usb.core.find(find_all=True)
        print("\nAvailable USB devices:")
        print("-" * 60)
        for device in devices:
            try:
                print(f"VID: 0x{device.idVendor:04x}, PID: 0x{device.idProduct:04x}")
                try:
                    print(f"  Manufacturer: {device.manufacturer}")
                    print(f"  Product: {device.product}")
                except Exception:
                    pass
            except Exception:
                pass
        print("-" * 60)
