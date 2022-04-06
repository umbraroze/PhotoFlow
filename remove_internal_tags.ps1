# Will remove image description and all tags, as these generally don't make much sense to anyone besides
# me for my own organisation scheme.
& exiftool.exe `
    -Comment= -Title= -Notes= -Description= -UserComment= -ImageDescription= -Caption-Abstract= `
    -Categories= -Keywords= -CatalogSets=  -Subject= -HierarchicalSubject= -TagsList= `
    $args[0]