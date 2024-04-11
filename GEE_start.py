## Google Earth engine setup/test

import ee
import google.auth
# ee.Authenticate()
# ee.Initialize()
#credentials, project_id = google.auth.default()
ee.Initialize(project='ee-joshuabuxton2018')
#ee.Initialize(credentials, project='ee-joshuabuxton2018')

print(ee.Image("NASA/NASADEM_HGT/001").get("title").getInfo())
