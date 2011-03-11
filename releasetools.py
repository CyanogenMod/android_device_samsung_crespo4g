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

import sha
import re

import common

def WriteRadioPatch(info, fn, size):
  info.script.AppendExtra(
    ('assert(samsung.write_firmware_image(package_extract_file("%s"),'
     '"%s"));') % (fn, size))

def FindRadioPatch(zipfile):
  try:
    radio_img = zipfile.read("RADIO/radio.pr.img.p")
  except KeyError:
    print "no radio.pr.img.p in target_files; skipping install"
    return None
  else:
    return radio_img

def FindRadio(zipfile):
  matches = []
  for name in zipfile.namelist():
    if re.match(r"^RADIO/radio[.](.+[.])?img$", name):
      matches.append(name)
  if len(matches) > 1:
    raise ValueError("multiple radio images in target-files zip!")
  if matches:
    print "using %s as radio.img" % (matches[0],)
    return zipfile.read(matches[0])
  else:
    return None

def FullOTA_InstallEnd(info):
  try:
    bootloader_img = info.input_zip.read("RADIO/bootloader.pr.img")
  except KeyError:
    print "full-no bootloader.pr.img in target_files; skipping install"
  else:
    common.ZipWriteStr(info.output_zip, "bootloader.pr.img", bootloader_img)
    info.script.Print("Writing bootloader...")
    info.script.WriteRawImage("/bootloader", "bootloader.pr.img")

  radio_img = FindRadio(info.input_zip)
  if not radio_img:
    print "full-no radio.pr.img in target_files; skipping install"
  else:
    print "full-radio.pr.img in target_files; included"
    common.ZipWriteStr(info.output_zip, "radio.pr.img", radio_img)
    info.script.Print("Writing radio...")
    WriteRadioPatch(info, "radio.pr.img", len(radio_img))

def IncrementalOTA_VerifyEnd(info):
  radio_img_p = FindRadioPatch(info.target_zip)
  if not radio_img_p: return
  info.script.CacheFreeSpaceCheck(len(radio_img_p))

def IncrementalOTA_InstallEnd(info):
  try:
    target_bootloader_img = info.target_zip.read("RADIO/bootloader.pr.img")
    try:
      source_bootloader_img = info.source_zip.read("RADIO/bootloader.pr.img")
    except KeyError:
      source_bootloader_img = None

    if source_bootloader_img == target_bootloader_img:
      print "inc-bootloader unchanged; skipping"
    else:
      common.ZipWriteStr(info.output_zip, "bootloader.pr.img", target_bootloader_img)
      info.script.Print("Writing bootloader...")
      info.script.WriteRawImage("/bootloader", "bootloader.pr.img")

  except KeyError:
    print "inc-no bootloader.pr.img in target target_files; skipping install"

  try:
    tf = common.File("radio.pr.img", info.target_zip.read("RADIO/radio.pr.img"))
    try:
      sf = common.File("radio.pr.img", info.source_zip.read("RADIO/radio.pr.img"))

      if tf.sha1 == sf.sha1:
        print "inc-radio image unchanged; skipping"
      else:
        diff = FindRadioPatch(info.target_zip)
        if not diff:
          print "inc-no radio.pr.img.p in target target_files;  include the whole target"
          tf.AddToZip(info.output_zip)
          info.script.Print("Writing radio...")
          WriteRadioPatch(info, "radio.pr.img", tf.size)
        else:
          print "inc-radio.pr.img.p in target target_files"
          common.ZipWriteStr(info.output_zip, "radio.pr.img.p", diff)
          info.script.Print("Patching radio...")
          WriteRadioPatch(info, "radio.pr.img.p", len(diff))

    except KeyError:
      # failed to read SOURCE radio image: include the whole target
      # radio image.
      print "inc-no radio.pr.img in target target_files; skipping install"

  except KeyError:
    # failed to read TARGET radio image: don't include any radio in update.
    print "inc-no radio.img in target target_files; skipping install"
