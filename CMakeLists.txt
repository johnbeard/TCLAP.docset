project(tclap-docset)
cmake_minimum_required(VERSION 3.12)

set(VERSION 1.2.2)
set(FEEDNAME "TCLAP")
set(BUNDLE_ID "TCLAP")

# Tarball URL
set(URL https://sourceforge.net/projects/tclap/files/tclap-${VERSION}.tar.gz)
set(URL_MD5 6f35665814dca292eceda007d7e13bcb)

# The configure command to run, if any
set(CONFIGURE_COMMAND ./configure)

# The directory of the doxygen build within the upstream src
set(UPSTREAM_DOC_DIR docs)

# The file in the upstream src that we will add the docset options to
# This might be a .in file, as patch is done before configure
set(DOXYFILE_MOD "Doxyfile.in")

# The file in the upstream src thatr doxygen will be called on
set(DOXYFILE "Doxyfile")

set(ZEAL_DB_OPTS --include-parent-scopes)

# Set the source images for each icon
set(ICON_SVG img/icon-16.svg)
set(ICON_SVG2X img/icon-16.svg)

# ------------------------------------------------------------------------------
## Should not need to change *too* much below here
# ------------------------------------------------------------------------------


find_program(DOXYTAG2ZEALDB doxytag2zealdb)
find_program(INKSCAPE inkscape)
find_program(PNGCRUSH pngcrush)

if(NOT DOXYTAG2ZEALDB)
    message(FATAL_ERROR "doxytag2zealdb not found.")
endif()

option(UPDATE_ICONS "Convert the icon SVG(s) to PNGs" OFF)

if(UPDATE_ICONS)
    if(NOT INKSCAPE)
        message(FATAL_ERROR "inkscape not found.")
    endif()

    if(NOT PNGCRUSH)
        message(FATAL_ERROR "pngcrush not found.")
    endif()
endif()

# output dir name for docset
set(DOCSET ${BUNDLE_ID}.docset)

include(ExternalProject)
ExternalProject_Add(upstream_src
    URL                 ${URL}
    URL_HASH            MD5=${URL_MD5}
    UPDATE_COMMAND      ""
    PATCH_COMMAND       ${CMAKE_SOURCE_DIR}/patch-doxyfile.sh
                        ${UPSTREAM_DOC_DIR}/${DOXYFILE_MOD} ${FEEDNAME} ${BUNDLE_ID}
    CONFIGURE_COMMAND   ${CONFIGURE_COMMAND} --prefix=${CMAKE_BINARY_DIR}
    BUILD_IN_SOURCE     1
    BUILD_COMMAND       ""
    INSTALL_COMMAND     ""
)

ExternalProject_Add_Step(upstream_src doxygen
  COMMAND           doxygen ${DOXYFILE}
  WORKING_DIRECTORY <SOURCE_DIR>/${UPSTREAM_DOC_DIR}
  COMMENT           "Building ${FEEDNAME} docs"
  DEPENDEES         build
)

# Build the Docset from the Doxygen-made makefile
# (this fails, but that's OK)
ExternalProject_Add_Step(upstream_src doxymake
  COMMAND           make || true
  WORKING_DIRECTORY <SOURCE_DIR>/${UPSTREAM_DOC_DIR}/html
  COMMENT           "Making ${FEEDNAME} docset"
  DEPENDEES         doxygen
)

ExternalProject_Add_Step(upstream_src zealdb
  COMMAND           ${DOXYTAG2ZEALDB} --tag ../${BUNDLE_ID}.tag
                    --db ${DOCSET}/Contents/Resources/docSet.dsidx
                    ${ZEAL_DB_OPTS}
  WORKING_DIRECTORY <SOURCE_DIR>/${UPSTREAM_DOC_DIR}/html
  COMMENT           "Constructing Zeal DB"
  DEPENDEES         doxymake
)

ExternalProject_Get_Property(upstream_src SOURCE_DIR)

set(DOCSET_COMPILED_DIR ${SOURCE_DIR}/${UPSTREAM_DOC_DIR}/html/${BUNDLE_ID}.docset)

# Collect stamp files to use as deps for archiving
set(STAMPS "")

# Icon generation

set(ICONS "")

function(gen_icon in out width)

    set(INPUT_FILE ${CMAKE_SOURCE_DIR}/${in})
    get_filename_component(SRCDIR ${INPUT_FILE} DIRECTORY)
    set(OUTPUT_FILE ${SRCDIR}/${out})

    if(UPDATE_ICONS)

        add_custom_command(
            COMMAND     ${INKSCAPE} --export-png=${OUTPUT_FILE}.tmp --export-width=${width} ${INPUT_FILE}
            COMMAND     ${PNGCRUSH} -brute ${OUTPUT_FILE}.tmp  ${OUTPUT_FILE}
            COMMAND     ${CMAKE_COMMAND} -E remove ${OUTPUT_FILE}.tmp
            OUTPUT      ${OUTPUT_FILE}
            DEPENDS     ${INPUT_FILE}
            COMMENT     "Exporting icon: ${out} @ ${width}px"
            VERBATIM
        )
    endif()

    set(ICONS ${ICONS} ${OUTPUT_FILE} PARENT_SCOPE)
endfunction(gen_icon)

gen_icon(${ICON_SVG} icon.png 16)
gen_icon(${ICON_SVG2X} icon@2x.png 32)

# Copy icons to docset
foreach(ICON ${ICONS})
    get_filename_component(ICONNAME ${ICON} NAME)
    add_custom_command(
        OUTPUT ${DOCSET_COMPILED_DIR}/${ICONNAME}
        COMMAND cp ${ICON} ${DOCSET_COMPILED_DIR}
        DEPENDS  ${ICONS} upstream_src
        COMMENT "Adding icon to the docset: ${ICONNAME}"
    )
    set(STAMPS ${STAMPS} ${DOCSET_COMPILED_DIR}/${ICONNAME})
endforeach()

# modify the Plist
set(PLIST ${DOCSET_COMPILED_DIR}/Contents/Info.plist)
set(PLIST_STAMP ${CMAKE_BINARY_DIR}/plist.stamp)
add_custom_command(
    OUTPUT ${PLIST_STAMP}
    COMMAND python ${CMAKE_SOURCE_DIR}/mod_plist.py
        -i ${PLIST}
        -o ${PLIST}
        -s "DocSetPlatformFamily" "${BUNDLE_ID}"
        -s "CFBundleName" "${BUNDLE_ID}"
        -t "isDashDocset"
        -s "dashIndexFilePath" "index.html"
        -v
    COMMAND ${CMAKE_COMMAND} -E touch ${PLIST_STAMP}
    DEPENDS  upstream_src
    COMMENT "Adjusting PList"
    VERBATIM
)
set(STAMPS ${STAMPS} ${PLIST_STAMP})

# Archive

set(OUTPUT_FILE ${CMAKE_BINARY_DIR}/${BUNDLE_ID}.tgz)

add_custom_command(
    COMMAND ${CMAKE_COMMAND} -E tar "cf" "${OUTPUT_FILE}" -- ${DOCSET}
    WORKING_DIRECTORY ${DOCSET_COMPILED_DIR}/..
    OUTPUT  ${OUTPUT_FILE}
    COMMENT "Compressing --> ${OUTPUT_FILE}."
    DEPENDS ${STAMPS}
    VERBATIM
)

add_custom_target(compress
    ALL
    DEPENDS ${OUTPUT_FILE}
)

add_custom_target(update
    COMMAND ${CMAKE_COMMAND} -E copy_directory ${DOCSET_COMPILED_DIR} ${CMAKE_SOURCE_DIR}/${DOCSET}
    COMMENT "Copying to ${CMAKE_SOURCE_DIR}"
    DEPENDS ${STAMPS}
    VERBATIM
)