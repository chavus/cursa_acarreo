"""
Version
v1.1 - June 2020 - Release
v1.2 - 09/13/2020 - Printing ticket and scanning tickets
"""

from cursa_acarreo import app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,  debug=True)
