# Copyright (C) 2010 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re

import common

def WriteRadio(info, radio_file):
  radio_file.AddToZip(info.output_zip)
  info.script.Print("Writing radio...")
  info.script.AppendExtra(
      'assert(samsung.update_modem(package_extract_file("%s")));\n' %
      (radio_file.name,))

def WriteBootloader(info, bootloader_file):
  bootloader_file.AddToZip(info.output_zip)
  info.script.Print("Writing bootloader...")
  info.script.WriteRawImage("/bootloader", bootloader_file.name)

def FindImage(zipfile, basename):
  matches = []
  for name in zipfile.namelist():
    m = re.match(r"^RADIO/(" + basename + "[.](.+[.])?img)$", name)
    if m:
      matches.append((name, m.group(1)))
  if len(matches) > 1:
    raise ValueError("multiple radio images in target-files zip!")
  if matches:
    matches = matches[0]
    print "using %s as %s" % matches
    return common.File(matches[1], zipfile.read(matches[0]))
  else:
    return None

def FullOTA_InstallEnd(info):
  bootloader_img = FindImage(info.input_zip, "bootloader")
  if bootloader_img:
    WriteBootloader(info, bootloader_img)
  else:
    print "no bootloader in target_files; skipping install"

  radio_img = FindImage(info.input_zip, "radio")
  if radio_img:
    WriteRadio(info, radio_img)
  else:
    print "no radio in target_files; skipping install"

def IncrementalOTA_InstallEnd(info):
  tf = FindImage(info.target_zip, "bootloader")
  sf = FindImage(info.source_zip, "bootloader")

  if not tf:
    print "no bootloader image in target target_files; skipping"
  elif sf and tf.sha1 == sf.sha1:
    print "bootloader image unchanged; skipping"
  else:
    WriteBootloader(info, sf)

  tf = FindImage(info.target_zip, "radio")
  sf = FindImage(info.source_zip, "radio")

  if not tf:
    print "no radio image in target target_files; skipping"
  elif sf and tf.sha1 == sf.sha1:
    print "radio image unchanged; skipping"
  else:
    WriteRadio(info, tf)
