import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import myapp

if __name__ == "__main__":
    myapp.run(host="0.0.0.0", port=80)

