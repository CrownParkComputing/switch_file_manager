import unittest
import os
import shutil
from pathlib import Path
from nsz.Fs.Nsp import Nsp
from nsz.Fs.Xci import Xci, XciStream
from nsz.Fs.Hfs0 import Hfs0
import hashlib

class TestMergeNspToXci(unittest.TestCase):
    def setUp(self):
        # Create test directories
        self.test_dir = Path("/home/jon/switch_file_manager/test_data")
        self.test_dir.mkdir(exist_ok=True)
        self.output_dir = self.test_dir / "output"
        self.output_dir.mkdir(exist_ok=True)
        self.temp_dir = self.test_dir / "temp"
        self.temp_dir.mkdir(exist_ok=True)

    def tearDown(self):
        # Only clean up temp directory, keep output
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_create_xci_from_nsp(self):
        # Test file - using demo NSP for testing
        demo_nsp = "/home/jon/Downloads/ztools/test_data/demo.nsp"
        
        # Extract NSP files
        nsp = Nsp(demo_nsp)
        nsp.open()
        print("\nExtracting NSP contents...")
        nsp.unpack(str(self.temp_dir))
        nsp.close()

        # Create XCI
        xci_path = str(self.output_dir / "test.xci")
        print("\nCreating XCI file...")
        with XciStream(xci_path, 'wb') as xci:
            # Set XCI header fields
            xci.magic = b'HEAD'
            xci.secureOffset = 0x4000
            xci.backupOffset = 0xffffffff
            xci.titleKekIndex = 0
            xci.gamecardSize = 0xE0
            xci.gamecardHeaderVersion = 0x2
            xci.gamecardFlags = 0x3
            xci.hfs0Offset = 0xF000

            # Create HFS0 header
            hfs0 = Hfs0()
            hfs0_data = bytearray()
            
            print("\nAdding files to HFS0...")
            # Add files from temp directory to HFS0
            for root, _, files in os.walk(str(self.temp_dir)):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, str(self.temp_dir))
                    print(f"Adding file: {rel_path}")
                    
                    with open(file_path, 'rb') as f:
                        data = f.read()
                        # Add file to HFS0
                        hfs0.addFile(rel_path, len(data))
                        hfs0_data.extend(data)

            print("\nWriting HFS0 header...")
            # Write HFS0 header
            hfs0_header = hfs0.getHeader()
            xci.write(hfs0_header)
            
            # Calculate and set HFS0 hashes
            xci.hfs0HeaderHash = hashlib.sha256(hfs0_header).digest()
            xci.hfs0InitialDataHash = hashlib.sha256(hfs0_data[:0x8000]).digest()
            
            print("\nWriting HFS0 data...")
            # Write HFS0 data
            xci.write(hfs0_data)

        # Verify XCI was created and has content
        self.assertTrue(os.path.exists(xci_path))
        file_size = os.path.getsize(xci_path)
        print(f"\nCreated XCI file size: {file_size / (1024*1024):.2f} MB")
        self.assertGreater(file_size, 0x10000)  # Should be at least 64KB
        
        # Verify XCI structure
        print("\nVerifying XCI structure...")
        xci = Xci()
        xci.open(xci_path)
        xci.printInfo()  # This will print the XCI structure for verification
        xci.close()

if __name__ == '__main__':
    unittest.main() 