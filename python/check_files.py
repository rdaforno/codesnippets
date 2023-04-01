#!/usr/bin/env python

# Calculates the checksum of all files within the specified search paths.
# The checksums will be stored in a file and can later be used to re-check the files (to e.g. detect bit-flips).

import sys
import os
import time


search_paths    = ["[my_path_1", "[my_path_2]"]    # a separate catalogue file will be created for each path
update_filelist = True


class ChecksumCatalogue:
    
    ignore_folders = ["@eaDir", "#recycle"]   # ignore (sub-)folders with these names
    ignore_fileext = []                       # file with these extensions will be skipped
    checksum_tool  = "md5sum"                 # which tool to use to calculate the checksum
    maxage_days    = 100                      # how old an entry may be before updating it
    
    def __init__(self, path):
        if not os.path.exists(path):
            print("invalid path " + path)
        self._path      = path
        self._filename  = path.replace('/', '_').strip() + "_checksums"
        self._catalogue = {}
        self._changed   = False
    
    def __len__(self):
        return len(self._catalogue)
        
    def calc_checksum(self, filename):
        if not os.path.isfile(filename):
            return 0
        res = os.popen(self.checksum_tool + ' "' + filename + '"').read()
        return res.split(' ')[0]

    def load_checksum(self):
        checksum_filename = self._filename + "_checksum"
        if not os.path.isfile(checksum_filename):
            return None
        with open(checksum_filename, "r") as f:
            checksum = f.readlines()[0].strip()
        return checksum
    
    def save_checksum(self):
        with open(self._filename + "_checksum", "w") as f:
            f.write(self.calc_checksum(self._filename))
        
    def load(self, ignore_corrupted=False):
        if not os.path.isfile(self._filename):
            print("file '%s' not found" % self._filename)
            return
        checksum1 = self.load_checksum()
        if not checksum1:
            print("cannot verify integrity of catalogue")
        else:
            checksum2 = self.calc_checksum(self._filename)
            if checksum1 != checksum2:
                print("invalid checksum, file %s is corrupted" % (self._filename))
                if not ignore_corrupted:
                    return
        with open(self._filename, "r") as f:
            lines = f.readlines()
            for line in lines:
                if line.strip() == "":
                    continue                
                parts = line.strip().split(':', 3)
                if len(parts) < 3:
                    continue
                self._catalogue[parts[0]] = (int(parts[1]), parts[2])
        self._changed = False
        print("catalogue loaded (%d items)" % len(self._catalogue))

    def save(self):
        sorted_catalogue = sorted(self._catalogue.items())    # sort dictionary by keys
        with open(self._filename, "w") as f:
            for elem in sorted_catalogue:
                (timestamp, checksum) = elem[1]
                if timestamp < 0:
                    continue
                f.write("%s:%d:%s\n" % (elem[0], timestamp, checksum))
        self.save_checksum()
        self._changed = False
        print("catalogue saved")

    def build(self):
        if not os.path.exists(self._path):
            print("path '%s' not found" % self._path)
            return
        print("searching for files in " + self._path + " ...")
        catalogue = {}
        try:
            for root, dirs, files in os.walk(self._path):
                ignore = False
                for ign in self.ignore_folders:
                    if ign in root:
                        ignore = True
                        break
                if not ignore:
                    for name in files:
                        if os.path.splitext(name)[1] not in self.ignore_fileext:
                            catalogue[os.path.join(root, name)] = (0, "0")
        except KeyboardInterrupt:
            sys.stdout.write("\b\b")
            return None
        return catalogue

    def update(self, save=True):
        new_catalogue = self.build()
        if not new_catalogue:
            return
        # add new files
        for key in new_catalogue:
            if key not in self._catalogue:
                print("new file added: %s" % key)
                self._catalogue[key] = (0, "0")
                self._changed = True
        # remove deleted files
        for key in self._catalogue:
            if key not in new_catalogue:
                print("file removed: %s" % key)
                self._catalogue[key] = (-1, "0")   # mark as invalid
                self._changed = True
        if self._changed and save:
            self.save()

    def check(self, save=True):
        aborted = False
        if not self._catalogue:
            return False
        print("updating catalogue %s ..." % (self._filename))
        sys.stdout.write("           ")
        timedelta = self.maxage_days * 86400
        try:
            cat_size = len(self._catalogue)
            progress = 0
            for item in self._catalogue:
                progress += 1
                (timestamp, checksum) = self._catalogue[item]
                if timestamp < 0:
                    continue
                sys.stdout.write("\b\b\b\b\b\b\b\b\b\b\b[ {:6.2f}% ]".format(progress * 100 / cat_size))
                sys.stdout.flush()
                if time.time() - timestamp > timedelta:
                    #print("[ {:6.2f}% ] calculating checksum of {} ...".format(progress * 100 / cat_size, item))
                    new_checksum = self.calc_checksum(item)
                    if checksum != "0" and checksum != new_checksum:
                        print("\nWARNING: checksum of file %s has changed (old: %s, new: %s)" % (item, checksum, new_checksum))
                    else:
                        self._catalogue[item] = (int(time.time()), new_checksum)
                        self._changed = True
        except KeyboardInterrupt:
            print("\b\b")
            aborted = True
        if self._changed and save:
            self.save()
        return not aborted
    
    def state(self):
        checked   = 0
        timedelta = self.maxage_days * 86400
        for item in self._catalogue:
            (timestamp, checksum) = self._catalogue[item]
            if time.time() - timestamp <= timedelta:
                checked += 1
        print("%d of %d items checked" % (checked, len(self._catalogue)))



if __name__ == "__main__":

    for path in search_paths:
        cat = ChecksumCatalogue(path)
        cat.load()
        if update_filelist:
            cat.update()
        if not cat.check():
            break
        #cat.state()
