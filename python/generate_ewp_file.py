#!/usr/bin/env python3
"""
Generates an EWARM / IAR project file (.ewp)

This file should be called from the root directory of the project.
"""

import sys
import os
import xml.etree.ElementTree as ET
import json
import xmltodict


# the following configuration is just an example, you will need to adjust it to your setup and needs

buildConfigs    = [ { "name" : "Debug", "debug" : 1, "mcu" : "LPC54102" } ] # one or more build configurations to create (MCU must be listen in the mcuConfigs dictionary below)

projectFilename = "myproject.ewp"                                           # output filename
srcPaths        = { "Source" : "src", "Include" : "inc" }                   # alias and path of all source folders (relative to the project root)
excludeDirs     = [ "templates" ]                                           # directories in srcPaths to ignore
excludeFiles    = [ ]                                                       # files in srcPaths to ignore
flattenDirs     = [ "inc" ]                                                 # don't create a tree structure for these folders
sourceFileTypes = [ ".cpp", ".h", ".c", ".s", "" ]                          # all other file types will be ignored
includePaths    = [ "$TOOLKIT_DIR$/CMSIS/Core/Include", "$PROJ_DIR$/inc" ]  # project includes
libPaths        = [ ]                                                       # libraries to include
preprocDefs     = [ ]                   # global preprocessor defines
groupExcludes   = { "Debug" : [ ] }     # groups (folders) to exclude from the build config
fileExcludes    = { "Debug" : [ ] }     # files to exclude from the build config

# dictionary with MCU-specific configuration values (to retrieve these values for your MCU, you may need to create an example project in IAR and inspect the ewp file)
mcuConfigs      = { "LPC54102" : {
                        "mcusel" : "LPC54102J512_M4	NXP LPC54102J512_M4",   # MCU description string as given by IAR (field 'OGChipSelectEditMenu' in the .ewp file)
                        "mcuid" : 39,                                       # MCU identification number as given by IAR (field 'CoreVariant' in the .ewp file)
                        "mcudefs" : [ "CPU_LPC54102J512BD64" ],             # required preprocessor defines for this MCU
                        "linkerfile" : "$PROJ_DIR$/LPC54102J512_M4.icf",    # linker filename
                        "fpuvs" : 4,                                        # if available: FPU version number as given by IAR (field 'FPU2' in the .ewp file)
                        "ignwarning" : "" },                                # warning to suppress
                  }


def reverseListDict(listDict):
    reverseDict = {}
    for key in listDict:
        for listelem in listDict[key]:
            reverseDict.setdefault(listelem, []).append(key)
    return reverseDict


exclFilesDict = reverseListDict(fileExcludes)
exclGroupsDict = reverseListDict(groupExcludes)


def main():
    configTree = []
    for config in buildConfigs:
        if config['mcu'] not in mcuConfigs:
            print("unknown MCU %s" % config['mcu'])
            continue
        configTree.append(getBuildSettings(config | mcuConfigs[config['mcu']]))
    # hint: to load a configuration from an existing .ewp file and convert it to json, use
    #       json.dumps(extractConfig(xmlToJson("myproject.ewp"), "Debug"), indent=4)

    fileTree = []
    for path in srcPaths:
        fileTree.append(buildFileDict(srcPaths[path], any([d in path for d in flattenDirs])) | { "name" : path })
    fileStructure = {
        "project" : {
            "fileVersion" : 3,
            "configuration" : configTree,
            "group" : fileTree
        }
    }    
    jsonToXml(fileStructure, projectFilename)


def getBuildSettings(config):
    defs = (config['mcudefs'] + preprocDefs) if config['debug'] else (["NDEBUG"] + config['mcudefs'] + preprocDefs)
    incl = [path.replace("$MCU$", config['mcu']) for path in includePaths]
    return {
        "name" : config['name'],
        "toolchain" : { "name" : "ARM" },
        "debug" : config['debug'],
        "settings" : [
        {
            "name" : "General",         # General options
            "archiveVersion" : 3,
            "data" : {
                "version" : 33,
                "wantNonLocal" : 1,
                "debug" : config['debug'],
                "option" : [
                    { "name" : "BrowseInfoPath", "state" : "$CONFIG_NAME$\BrowseInfo" },
                    { "name" : "ExePath", "state" : "$CONFIG_NAME$\Exe" },
                    { "name" : "ObjPath", "state" : "$CONFIG_NAME$\Obj" },
                    { "name" : "ListPath", "state" : "$CONFIG_NAME$\List" },
                    { "name" : "GEndianMode", "state" : 0 },                        # 0 = little endian
                    { "name" : "Input description", "state" : "Full formatting, without multibyte support." },  # scanf description
                    { "name" : "Output description", "state" : "Full formatting, without multibyte support." }, # printf description
                    { "name" : "GOutputBinary", "state" : 0 },                      # output type: 0 = executable
                    { "name" : "OGCoreOrChip", "state" : 1 },                       # processor variant type: 1 = device
                    { "name" : "GRuntimeLibSelect", "version" : 0, "state" : 1 },   # library: 1 = Normal
                    { "name" : "GRuntimeLibSelectSlave", "version" : 0, "state" : 1 },
                    { "name" : "RTDescription", "state" : "Use the normal configuration of the C/C++ runtime library. No locale interface, C locale, no file descriptor support, no multibytes in printf and scanf, and no hex floats in strtod." },     # library description
                    { "name" : "OGProductVersion", "state" : "5.10.0.159" },
                    { "name" : "OGLastSavedByProductVersion", "state" : "9.10.1.36322" },                       # IAR version
                    { "name" : "OGChipSelectEditMenu", "state" : config['mcusel'] },                            # selected MCU (string)
                    { "name" : "GenLowLevelInterface", "state" : 0 },               # low-level interface implementation: 0 = None
                    { "name" : "GEndianModeBE", "state" : 1 },                      # 1 = BE8
                    { "name" : "OGBufferedTerminalOutput", "state" : 0 },           # buffered terminal output disabled
                    { "name" : "GenStdoutInterface", "state" : 0 },                 # stdout/stderr: 0 = via semihosting
                    { "name" : "RTConfigPath2", "state" : "$TOOLKIT_DIR$\inc\c\DLib_Config_Normal.h" },         # library configuration file
                    { "name" : "GBECoreSlave", "version" : 29, "state" : config['mcuid'] },
                    { "name" : "OGUseCmsis", "state" : 0 },                         # don't use CMSIS
                    { "name" : "OGUseCmsisDspLib", "state" : 0 },                   # don't use CMSIS DSP extension
                    { "name" : "GRuntimeLibThreads", "state" : 0 },                 # thread support in library disabled
                    { "name" : "CoreVariant", "version" : 29, "state" : config['mcuid'] },                      # processor variant (IAR ID) 
                    { "name" : "GFPUDeviceSlave", "state" : config['mcusel'] },                                 # selected MCU (string)
                    { "name" : "FPU2", "version" : 0, "state" : config['fpuvs'] },  # FPU: 4 = VFPv4, 6 = VFPv5
                    { "name" : "NrRegs", "version" : 0, "state" : 1 },              # D registers: 1 = 16
                    { "name" : "NEON", "state" : 0 },                               # Advanced SIMD disabled
                    { "name" : "GFPUCoreSlave2", "version" : 29, "state" : config['mcuid'] },
                    { "name" : "OGCMSISPackSelectDevice" },
                    { "name" : "OgLibHeap", "state" : 0 },                          # heap selection: 0 = automatic
                    { "name" : "OGLibAdditionalLocale", "state" : 0 },              # additional locale support disabled
                    { "name" : "OGPrintfVariant", "version" : 0, "state" : 1 },     # printf formatter: 1 = Full
                    { "name" : "OGPrintfMultibyteSupport", "state" : 0 },           # multibyte support disabled
                    { "name" : "OGScanfVariant", "version" : 0, "state" : 1 },      # scanf formatter: 1 = Full
                    { "name" : "OGScanfMultibyteSupport", "state" : 0 },            # multibyte support disabled
                    { "name" : "GenLocaleTags", "state" : "" },
                    { "name" : "GenLocaleDisplayOnly", "state" : "" },
                    { "name" : "DSPExtension", "state" : 1 },                       # enabled
                    { "name" : "TrustZone", "state" : 0 },                          # disabled
                    { "name" : "TrustZoneModes", "version" : 0, "state" : 0 },      # 0 = secure
                    { "name" : "OGAarch64Abi", "state" : 0 },                       # data model: 0 = ILP32
                    { "name" : "OG_32_64Device", "state" : 0 },                     # execution mode: 0 = 32-bit
                ],
            },
        },
        {
            "name" : "ICCARM",          # C/C++ Compiler
            "archiveVersion" : 2,
            "data" : {
                "version": 37,
                "wantNonLocal" : 1,
                "debug" : config['debug'],
                "option" : [
                    { "name" : "CCOptimizationNoSizeConstraints", "state" : 0 },    # no size constraints: 0 = disabled
                    { "name" : "CCDefines", "state" : defs },                       # defined symbols (preprocessor defines)
                    { "name" : "CCPreprocFile", "state" : config['debug'] },        # preprocessor output to file: 0 = no, 1 = yes
                    { "name" : "CCPreprocComments", "state" : config['debug'] },    # preserve comments in preprocessor output
                    { "name" : "CCPreprocLine", "state" : config['debug'] },        # generate #line directives in preproc output
                    { "name" : "CCListCFile", "state" : 0 },                        # output list file: 0 = no
                    { "name" : "CCListCMnemonics", "state" : 0 },                   # assembler mnemonics
                    { "name" : "CCListCMessages", "state" : 0 },                    # diagnostics
                    { "name" : "CCListAssFile", "state" : 0 },                      # output assembler file: 0 = no
                    { "name" : "CCListAssSource", "state" : 0 },                    # include source in assembler output
                    { "name" : "CCEnableRemarks", "state" : 0 },                    # enable remarks: 0 = disabled
                    { "name" : "CCDiagSuppress", "state" : config['ignwarning'] },  # diagnostics / warnings to suppress
                    { "name" : "CCDiagRemark", "state" : "" },                      # treat as remarks
                    { "name" : "CCDiagWarning", "state" : "" },                     # treat as warnings
                    { "name" : "CCDiagError", "state" : "" },                       # treat as errors
                    { "name" : "CCObjPrefix", "state" : 1 },
                    { "name" : "CCAllowList", "version" : 1, "state" : "00000000" if config['debug'] else "11111110" }, # enabled transformations (optimization)
                    { "name" : "CCDebugInfo", "state" : config['debug'] },
                    { "name" : "IEndianMode", "state" : 1 },
                    { "name" : "IProcessor", "state" : 1 },
                    { "name" : "IExtraOptionsCheck", "state" : 0 },
                    { "name" : "IExtraOptions", "state" : "" },
                    { "name" : "CCLangConformance", "state" : 0 },                  # language conformance: 0 = standard with IAR extensions
                    { "name" : "CCSignedPlainChar", "state" : 0 },                  # plain char is: 0 = signed
                    { "name" : "CCRequirePrototypes", "state" : 0 },                # require prototypes: 0 = no
                    { "name" : "CCDiagWarnAreErr", "state" : 1 },                   # treat warnings as errors: 1 = yes
                    { "name" : "CCCompilerRuntimeInfo", "state" : 0 },
                    { "name" : "IFpuProcessor", "state" : 1 },
                    { "name" : "OutputFile", "state" : "$FILE_BNAME$.o" },
                    { "name" : "CCLibConfigHeader", "state" : 1 },
                    { "name" : "PreInclude", "state" : "" },                        # preinclude file
                    { "name" : "CCIncludePath2", "state" : incl },                  # additonal include directories
                    { "name" : "CCStdIncCheck", "state" : 0 },                      # ignore standard include directories: 0 = disabled
                    { "name" : "CCCodeSection", "state" : ".text" },                # code section name
                    { "name" : "IProcessorMode2", "state" : 1 },                    # processor mode: 1 = Thumb
                    { "name" : "CCOptLevel", "state" : 0 if config['debug'] else 3 },       # optimization level: 0 = none, 3 = high
                    { "name" : "CCOptStrategy", "version" : 0, "state" : 0 },               # optimization strategy: 0 = balanced
                    { "name" : "CCOptLevelSlave", "state" : 0 if config['debug'] else 3 },
                    { "name" : "CCPosIndRopi", "state" : 0 },                       # code read-only data (ropi): 0 = disabled
                    { "name" : "CCPosIndRwpi", "state" : 0 },                       # read/write data (rwpi): 0 = disabled
                    { "name" : "CCPosIndNoDynInit", "state" : 0 },                  # no dynamic read/write init: 0 = disabled
                    { "name" : "IccLang", "state" : 2 },                            # language: 0 = C, 1 = C++, 2 = auto (extension-based)
                    { "name" : "IccCDialect", "state" : 1 },                        # C dialect: 1 = standard C
                    { "name" : "IccAllowVLA", "state" : 0 },                        # don't allow VLA
                    { "name" : "IccStaticDestr", "state" : 1 },                     # destroy static objects: 1 = yes
                    { "name" : "IccCppInlineSemantics", "state" : 0 },              # C++ inline semantics disabled
                    { "name" : "IccCmsis", "state" : 1 },
                    { "name" : "IccFloatSemantics", "state" : 0 },                  # floating-point semantics: 0 = strict
                    { "name" : "CCNoLiteralPool", "state" : 0 },
                    { "name" : "CCOptStrategySlave", "version" : 0, "state" : 0 },
                    { "name" : "CCGuardCalls", "state" : 1 },
                    { "name" : "CCEncSource", "state" : 2 },                        # source file encoding: 2 = UTF-8
                    { "name" : "CCEncOutput", "state" : 2 },                        # output file encoding: 2 = UTF-8
                    { "name" : "CCEncOutputBom", "state" : 1 },                     # with BOM: 1 = yes
                    { "name" : "CCEncInput", "state" : 1 },                         # input file encoding: 1 = UTF-8
                    { "name" : "IccExceptions2", "state" : 0 },
                    { "name" : "IccRTTI2", "state" : 1 },                           # enable RTTI: 1 = yes
                    { "name" : "OICompilerExtraOption", "state" : 1 },
                    { "name" : "CCStackProtection", "state" : 0 },
                ],
            },
        },
        { 
            "name" : "AARM",            # Assembler
            "archiveVersion" : 2,
            "data" : {
                "version" : 11,
                "wantNonLocal" : 1,
                "debug" : config['debug'],
                "option" : [
                    { "name" : "AObjPrefix", "state" : 1 },
                    { "name" : "AEndian", "state" : 1 },
                    { "name" : "ACaseSensitivity", "state" : 1 },                   # user symbols are case sensitive: 1 = yes
                    { "name" : "MacroChars", "version" : 0, "state" : 0 },          # macro quote characters: 0 = <>
                    { "name" : "AWarnEnable", "state" : 0 },                        # enable warnings: 0 = enabled
                    { "name" : "AWarnWhat", "state" : 0 },                          # warn level: 0 = all
                    { "name" : "AWarnOne", "state" : "" },
                    { "name" : "AWarnRange1", "state" : "" },
                    { "name" : "AWarnRange2", "state" : "" },
                    { "name" : "ADebug", "state" : config['debug'] },               # generate debug information
                    { "name" : "AltRegisterNames", "state" : 0 },                   # allow alternative register names: 0 = no
                    { "name" : "ADefines", "state" : "" },                          # defined symbols
                    { "name" : "AList", "state" : 0 },                              # output list file: 0 = no
                    { "name" : "AListHeader", "state" : 1 },                        # include header: 1 = yes
                    { "name" : "AListing", "state" : 1 },                           # include listing: 1 = yes
                    { "name" : "Includes", "state" : 0 },
                    { "name" : "MacDefs", "state" : 0 },
                    { "name" : "MacExps", "state" : 1 },
                    { "name" : "MacExec", "state" : 0 },
                    { "name" : "OnlyAssed", "state" : 0 },
                    { "name" : "MultiLine", "state" : 0 },
                    { "name" : "PageLengthCheck", "state" : 0 },
                    { "name" : "PageLength", "state" : 80 },
                    { "name" : "TabSpacing", "state" : 8 },
                    { "name" : "AXRef", "state" : 0 },
                    { "name" : "AXRefDefines", "state" : 0 },
                    { "name" : "AXRefInternal", "state" : 0 },
                    { "name" : "AXRefDual", "state" : 0 },
                    { "name" : "AProcessor", "state" : 1 },
                    { "name" : "AFpuProcessor", "state" : 1 },
                    { "name" : "AOutputFile", "state" : "$FILE_BNAME$.o" },
                    { "name" : "ALimitErrorsCheck", "state" : 0 },
                    { "name" : "ALimitErrorsEdit", "state" : 100 },
                    { "name" : "AIgnoreStdInclude", "state" : 0 },                  # ignore standard include directories
                    { "name" : "AUserIncludes", "state" : "" },                     # additional include directories
                    { "name" : "AExtraOptionsCheckV2", "state" : 0 },               # use command line options
                    { "name" : "AExtraOptionsV2", "state" : "" },                   # command line options
                    { "name" : "AsmNoLiteralPool", "state" : 0 },                   # no data reads in code memory: 0 = disabled
                    { "name" : "PreInclude", "state" : "" },                        # preinclude file
                ],
            },
        },
        {
            "name" : "OBJCOPY",         # Output Converter
            "archiveVersion" : 0,
            "data" : {
                "version" : 1,
                "wantNonLocal" : 1,
                "debug" : config['debug'],
                "option" : [
                    { "name" : "OOCOutputFormat", "version" : 3, "state" : 1 },     # output format: 1 = Intel extended hex
                    { "name" : "OCOutputOverride", "state" : 1 },                   # override default: 1 = yes
                    { "name" : "OOCOutputFile", "state" : "$PROJ_FNAME$.hex" },     # override output file name
                    { "name" : "OOCCommandLineProducer", "state" : 1 },
                    { "name" : "OOCObjCopyEnable", "state" : 1 },
                ],
            },
        },
        {
            "name" : "CUSTOM",          # Custom Build
            "archiveVersion" : 3,
            "data" : {
                "extensions" : "",
                "cmdline" : "",
                "hasPrio" : 1,                                                      # ? set by IAR to seemingly random value
                "buildSequence" : "preCompile",                                     # run before compiling / assembling
            },
        },
        {
            "name" : "BUILDACTION",     # Build Actions
            "archiveVersion" : 1,
            "data" : {
                "prebuild" : "",                                                    # pre-build script
                "postbuild" : "",
            },
        },
        {
            "name" : "ILINK",           # Linker
            "archiveVersion" : 0,
            "data" : {
                "version" : 25,
                "wantNonLocal" : 1,
                "debug" : config['debug'],
                "option" : [
                    { "name" : "IlinkOutputFile", "state" : "$PROJ_FNAME$.out" },   # output filename
                    { "name" : "IlinkLibIOConfig", "state" : 1 },
                    { "name" : "IlinkInputFileSlave", "state" : 0 },
                    { "name" : "IlinkDebugInfoEnable", "state" : 1 },               # include debug information in output
                    { "name" : "IlinkKeepSymbols", "state" : "" },
                    { "name" : "IlinkRawBinaryFile", "state" : "" },
                    { "name" : "IlinkRawBinarySymbol", "state" : "" },
                    { "name" : "IlinkRawBinarySegment", "state" : "" },
                    { "name" : "IlinkRawBinaryAlign", "state" : "" },
                    { "name" : "IlinkDefines", "state" : "" },
                    { "name" : "IlinkConfigDefines", "state" : "" },
                    { "name" : "IlinkMapFile", "state" : 1 },                       # generate linker map file: 1 = yes
                    { "name" : "IlinkLogFile", "state" : 0 },                       # generate log file: 0 = no
                    { "name" : "IlinkLogInitialization", "state" : 0 },
                    { "name" : "IlinkLogModule", "state" : 0 },
                    { "name" : "IlinkLogSection", "state" : 0 },
                    { "name" : "IlinkLogVeneer", "state" : 0 },
                    { "name" : "IlinkIcfOverride", "state" : 1 },
                    { "name" : "IlinkIcfFile", "state" : config['linkerfile'] },
                    { "name" : "IlinkIcfFileSlave", "state" : "" },
                    { "name" : "IlinkEnableRemarks", "state" : 0 },
                    { "name" : "IlinkSuppressDiags", "state" : "" },
                    { "name" : "IlinkTreatAsRem", "state" : "" },
                    { "name" : "IlinkTreatAsWarn", "state" : "" },
                    { "name" : "IlinkTreatAsErr", "state" : "" },
                    { "name" : "IlinkWarningsAreErrors", "state" : 0 },
                    { "name" : "IlinkUseExtraOptions", "state" : 0 },
                    { "name" : "IlinkExtraOptions", "state" : "" },
                    { "name" : "IlinkLowLevelInterfaceSlave", "state" : 1 },
                    { "name" : "IlinkAutoLibEnable", "state" : 1 },                 # automatic runtime library selection: 1 = yes
                    { "name" : "IlinkAdditionalLibs", "state" : libPaths },
                    { "name" : "IlinkOverrideProgramEntryLabel", "state" : 0 },     # override default program entry: 0 = no
                    { "name" : "IlinkProgramEntryLabelSelect", "state" : 0 },
                    { "name" : "IlinkProgramEntryLabel", "state" : "__iar_program_start" },
                    { "name" : "DoFill", "state" : 0 },
                    { "name" : "FillerByte", "state" : "0xFF" },
                    { "name" : "FillerStart", "state" : "0x0" },
                    { "name" : "FillerEnd", "state" : "0x0" },
                    { "name" : "CrcSize", "version" : 0, "state" : 1 },
                    { "name" : "CrcAlign", "state" : 1 },
                    { "name" : "CrcPoly", "state" : "0x11021" },
                    { "name" : "CrcCompl", "version" : 0, "state" : 0 },
                    { "name" : "CrcBitOrder", "version" : 0, "state" : 0 },
                    { "name" : "CrcInitialValue", "state" : "0x0" },
                    { "name" : "DoCrc", "state" : 0 },
                    { "name" : "IlinkBE8Slave", "state" : 1 },
                    { "name" : "IlinkBufferedTerminalOutput", "state" : 1 },
                    { "name" : "IlinkStdoutInterfaceSlave", "state" : 1 },
                    { "name" : "CrcFullSize", "state" : 0 },
                    { "name" : "IlinkIElfToolPostProcess", "state" : 0 },
                    { "name" : "IlinkLogAutoLibSelect", "state" : 0 },
                    { "name" : "IlinkLogRedirSymbols", "state" : 0 },
                    { "name" : "IlinkLogUnusedFragments", "state" : 0 },
                    { "name" : "IlinkCrcReverseByteOrder", "state" : 0 },
                    { "name" : "IlinkCrcUseAsInput", "state" : 1 },
                    { "name" : "IlinkOptInline", "state" : 1 - config['debug'] },           # inline small routines: 0 = no, 1 = yes
                    { "name" : "IlinkOptExceptionsAllow", "state" : config['debug'] },      # allow C++ exceptions: 0 = no
                    { "name" : "IlinkOptExceptionsForce", "state" : 0 },
                    { "name" : "IlinkCmsis", "state" : 1 },
                    { "name" : "IlinkOptMergeDuplSections", "state" : 0 },          # merge duplicate sections: 0 = no
                    { "name" : "IlinkOptUseVfe", "state" : 1 },                     # perform virtual function eliminiation: 1 = yes
                    { "name" : "IlinkOptForceVfe", "state" : 0 },                   # force even if modules are missing VFE info: 0 = no
                    { "name" : "IlinkStackAnalysisEnable", "state" : config['debug'] },     # stack usage analysis: 1 = enable
                    { "name" : "IlinkStackControlFile", "state" : "" },
                    { "name" : "IlinkStackCallGraphFile", "state" : "" },
                    { "name" : "CrcAlgorithm", "version" : 1, "state" : 1 },
                    { "name" : "CrcUnitSize", "version" : 0, "state" : 0 },
                    { "name" : "IlinkThreadsSlave", "state" : 1 },
                    { "name" : "IlinkLogCallGraph", "state" : 0 },
                    { "name" : "IlinkIcfFile_AltDefault", "state" : "" },
                    { "name" : "IlinkEncInput", "state" : 1 },                      # input file encoding: 1 = UTF-8
                    { "name" : "IlinkEncOutput", "state" : 1 },                     # text output file encoding: 1 = UTF-8
                    { "name" : "IlinkEncOutputBom", "state" : 1 },
                    { "name" : "IlinkHeapSelect", "state" : 1 },
                    { "name" : "IlinkLocaleSelect", "state" : 1 },
                    { "name" : "IlinkTrustzoneImportLibraryOut", "state" : "$PROJ_FNAME$_import_lib.o" },
                    { "name" : "OILinkExtraOption", "state" : 1 },
                    { "name" : "IlinkRawBinaryFile2", "state" : "" },
                    { "name" : "IlinkRawBinarySymbol2", "state" : "" },
                    { "name" : "IlinkRawBinarySegment2", "state" : "" },
                    { "name" : "IlinkRawBinaryAlign2", "state" : "" },
                    { "name" : "IlinkLogCrtRoutineSelection", "state" : 0 },
                    { "name" : "IlinkLogFragmentInfo", "state" : 0 },
                    { "name" : "IlinkLogInlining", "state" : 0 },
                    { "name" : "IlinkLogMerging", "state" : 0 },
                    { "name" : "IlinkDemangle", "state" : 0 },
                ],
            },
        },
        {
            "name" : "IARCHIVE",
            "archiveVersion" : 0,
            "data" : {
                "version" : 0,
                "wantNonLocal" : 1,
                "debug" : config['debug'],
                "option" : [
                    { "name" : "IarchiveInputs", "state" : "" },
                    { "name" : "IarchiveOverride", "state" : 0 },
                    { "name" : "IarchiveOutput", "state" : "###Unitialized###" },
                ],
            },
        },
        {
            "name" : "Coder",
            "archiveVersion" : 0,
            "data" : {},
        },
        ]
    }


def jsonToXml(jsonData, outputFilename):
    with open(outputFilename, 'w') as xmlFile:
        xmltodict.unparse(jsonData, output=xmlFile, pretty=True, indent='    ')   # other options: short_empty_elements


def xmlToJson(inputFilename):
    with open(inputFilename, 'r') as xmlFile:
        return xmltodict.parse(xmlFile.read())


def extractConfig(js, config):
    for conf in js['project']['configuration']:
        if conf['name'] == config:
            return conf
    return None


def buildFileDict(path, flatten = False):
    fileDict = { "name" : os.path.basename(path), "group" : [], "file" : [] }
    for file in os.listdir(path):
        fileWithPath = path + '/' + file
        if os.path.isdir(fileWithPath):
            if not any([subdir in fileWithPath for subdir in excludeDirs]):
                group = { "name" : file }
                if file in exclGroupsDict:
                    group['excluded'] = { "configuration" : exclGroupsDict[file] }
                flattenCurr = flatten or any([d in fileWithPath for d in flattenDirs])
                subDirDict = buildFileDict(fileWithPath, flattenCurr)
                if subDirDict['group'] or subDirDict['file']:
                    if flattenCurr:
                        fileDict['file'].extend(subDirDict['file'])
                    else:
                        fileDict['group'].append(group | subDirDict)
        elif os.path.isfile(fileWithPath):
            if os.path.splitext(file)[1] in sourceFileTypes and not file in excludeFiles:
                fileEntry = { "name" : "$PROJ_DIR$\\" + fileWithPath.replace('/', '\\') }
                if file in exclFilesDict:
                    fileEntry['excluded'] = { "configuration" : exclFilesDict[file] }
                fileDict["file"].append(fileEntry)
                continue
    return fileDict


if __name__ == '__main__':
    main()
