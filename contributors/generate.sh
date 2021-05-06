#!/bin/bash

# Given a repository path and a file pattern, generate data for each set
# of commits relevant to files that match the pattern, save to a directory
# here, and then further parse and generate an interface to visualize it.

here="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# We must have two arguments
if [ $# -lt 4 ]; then
    printf "You must provide a repository name, repository path, search path, and file pattern."
    exit 1
fi

name="$1"
repository="$2"
searchpath="$3"
pattern="$4"

# Sanity checks
printf "name: $name\n"
printf "repo: $repository\n"
printf "searchpath: $searchpath\n"
printf "pattern: $pattern\n"

# The repository must exist
if [ ! -d "$repository" ]; then
    printf "$respository does not exist.\n"
fi
# create a data directory
mkdir -p $here/data

fullpath=$(readlink -f $repository)

# Add the bin with spack to the path
export PATH=$fullpath/bin:$PATH

# Function to derive package name
function getpackage() {
    filename=$1
    package=$(dirname $filename)
    package=$(basename $package)
    echo $package
}

cd $repository
for filename in $(find $searchpath -name "$pattern"); do
    package=$(getpackage $filename)
    outfile="$here/data/${package}.json"
    if [ -f "$outfile" ]; then
        continue
    fi
    printf "Parsing $package: $filename\n"
    # requires PR with addition of --json flag
    spack blame --json $package > "$outfile"
done
