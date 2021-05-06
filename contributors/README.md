# Contributors per Package

In this case of popularity assessment, we are looking at the number of
contributors per package. We can easily assess this with spack blame.
As with the [commits](../commits) metric, we will use the same spack
commit to do the assessment.

## 1. How many people have contributed to each package?

This can be fairly easy done with `spack blame`, and we use the [generate.sh](generate.sh) 
script to generate our data file:

```bash
# We must use the fullpath of the repository
repository=$HOME/Desktop/Code/spack
              # name      # root    # relative search folder          # file pattern
./generate.sh spack/spack $repository var/spack/repos/builtin/packages/ package.py
```

The results are written to [data/commits](data/commits) and organized by package
file.  At the time of parsing, this is the latest commit:

```
commit 0250a0d4ce921513bea05baca954fbcabf695ef4 (HEAD -> develop, origin/develop, origin/HEAD)
Author: Itaru Kitayama <ikitayama@users.noreply.github.com>
Date:   Mon May 3 01:04:18 2021 +0900

    scalasca: Update variant releases (#23383)
    
    * Add 4.6
    
    * Add Cubelib 4.6
    
    Co-authored-by: Itaru Kitayama <itaru.kitayama@riken.jp>
```

We next want to generate a summary of counts for each package, by month
and year, and render this into a template to show our results.
This script also requires spack-python to so we can
map packages to build systems:

```bash
spack python summarize-contributions.py data/
```

Currently, the interface generated is [index.html](index.html). It looks like there
was a re-organization of packages, so the data from 2013 looks a little strange.
