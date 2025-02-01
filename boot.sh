#!/bin/bash
flask db upgrade
exec waitress-serve --port=5000 --threads=50 control_saz:app