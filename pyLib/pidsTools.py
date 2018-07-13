import netCDF4 as nc
import sys
import argparse
import numpy as np
import ConfigParser
from itertools import islice, chain, repeat

from netcdfTools import *
from mapTools import readNumpyZTile


'''
Author:
Sasu Karttunen
sasu.karttunen@helsinki.fi
Institute for Atmospheric and Earth System Research (INAR) / Physics
University of Helsinki
'''

# =*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*

def setPIDSGlobalAtrributes(ds, globalAttributes):
  ''' Set PIDS global attributes to data set file '''
  strAttributeKeys = ['Conventions', 'palm_version', 'title', 'acronym', 'campaign',\
                   'institution', 'author', 'contact_person', 'licence', 'history',\
                   'keywords', 'references', 'comment', 'data_content', 'source',\
                   'dependencies', 'location', 'site']
  floatAttributeKeys = ['origin_x', 'origin_y', 'origin_z', 'origin_lat', 'origin_lon',\
                        'rotation_angle', 'origin_time']
  for key in strAttributeKeys:
    try:
      setattr(ds, key, globalAttributes[key])
    except KeyError:
      if(getattr(ds, key, "")==""):
        setattr(ds, key, "")

  for key in floatAttributeKeys:
    try:
      setattr(ds, key, float(globalAttributes[key]))
    except KeyError:
      if(getattr(ds, key, 0.0)==0.0):
        setattr(ds, key, 0.0)

#=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*

def readConfigSection(config, name):
  ''' Prints and returns variables found from given section '''
  try:
    configSection = config._sections[name]
  except KeyError:
    return None

  del configSection['__name__']
  for attr, val in configSection.iteritems():
    print("{}: {}".format(attr,val))

  return configSection

#=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*

def readConfigVariable(config, section, name):
  try:
    var = config.get(section, name)
  except ConfigParser.NoOptionError:
    return None

  return var


#=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*

def parseStringArrayInput(input_str, dtype):
  # Return string type input as 2D numpy array
  # Example input: "2,5,6\n3,6,7\n6,7,9"
  # Example output np.array([[2,5,6],[3,6,7],[6,7,9]])
  rows = input_str.split("\n")
  if(len(rows[0].split(","))==1):
    rows=rows[1:]
  arr = np.zeros((len(rows),len(rows[0].split(","))),dtype=dtype)
  for i in xrange(len(rows)):
    items = rows[i].split(",")
    try:
      arr[i,:]=np.array(map(dtype, items))
    except ValueError:
      continue

  return arr

#=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*

def parseCharacterArray(input_str, maxstrlen):
  # Return string type input as 2D character array
  # Example input: "abba,cd,acdc"
  # Example output np.array([['a','b','b','a'],['c','d','',''],['a','c','d','c']])
  items = input_str.split(",")
  charr = map(list, items)
  # Fill missing elements with empty char and construct a 2d array
  def pad_array(charr):
    return list(islice(chain(charr, repeat('')),maxstrlen))
  charr = np.array(map(pad_array,charr))
  return charr

#=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
#                    UNIVERSAL                      #
#=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*

def createXDim(ds, nPx, dPx, dims):
  # Creates a new x-axis unless it already exists
  if('x' not in dims):
    x_dim = createCoordinateAxis(ds, nPx, dPx, 0, 'x', 'f4', 'm', True, False, verbose=False)
    x_dim.long_name = "distance to origin in x-direction"
    dims.append('x')
    return x_dim
  else:
    x_dim = ds.variables['x']
    return x_dim

#=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*

def createYDim(ds, nPx, dPx, dims):
  # Creates a new y-axis unless it already exists
  if('y' not in dims):
    y_dim = createCoordinateAxis(ds, nPx, dPx, 1, 'y', 'f4', 'm', True, False, verbose=False)
    y_dim.long_name = "distance to origin in y-direction"
    dims.append('y')
    return y_dim
  else:
    y_dim = ds.variables['y']
    return y_dim

#=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*

def createZDim(ds, nPx, dPx, dims):
  # Creates a new z-axis unless it already exists
  if('z' not in dims):
    z_dim = createCoordinateAxis(ds, nPx, dPx, 2, 'z', 'f4', 'm', True, False, verbose=False)
    z_dim.long_name = "height above origin"
    dims.append('z')
    return z_dim
  else:
    z_dim = ds.variables['z']
    return z_dim

#=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
#                   PIDS_STATIC                     #
#=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*

def createZLADDim(ds, nPx, dPx, dims):
  # Creates a new zlad-axis unless it already exists
  if('zlad' not in dims):
    zlad_dim = createCoordinateAxis(ds, nPx, dPx, 2, 'zlad', 'f4', 'm', True, False, verbose=False)
    zlad_dim.long_name = "height above origin"
    dims.append('zlad')
    return zlad_dim
  else:
    zlad_dim = ds.variables['zlad']
    return zlad_dim

#=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*

def processOrography(fname,ds,vars,dims):
  # Write orography data to given ds
  oroDict = readNumpyZTile(fname,verbose=False)
  oroR = oroDict['R']
  oroDPx = oroDict['dPx']
  oroNPx = np.shape(oroR)

  if('zt' in vars):
    ds.variables['zt'][:]=oroR
    return ds.variables['zt']
  else:
    # Create new dimensions or check if the orography matches old ones
    x_dim = createXDim(ds, oroNPx, oroDPx, dims)
    y_dim = createYDim(ds, oroNPx, oroDPx, dims)

    oroNCVar = createNetcdfVariable(ds, oroR, 'zt', 0, 'm', 'f4', ('y','x'), False, False, fill_value=-9999.9, verbose=False)
    oroNCVar.long_name= "terrain_height"

    return oroNCVar

#=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*

def processBuildings(fname,ds,vars,dims):
  buildDict = readNumpyZTile(fname,verbose=False)
  buildR = buildDict['R']
  buildDPx = buildDict['dPx']
  buildNPx = np.shape(buildR)
  buildLOD = len(buildNPx)-1 # 1=2D height field, 2=3D mask

  if(buildLOD==1):
    # Save as a 2D building height array
    if('buildings_2d' in vars):
      ds.variables['buildings_2d'][:]=buildR
      return ds.variables['buildings_2d']
    else:
      x_dim = createXDim(ds, buildNPx, buildDPx, dims)
      y_dim = createYDim(ds, buildNPx, buildDPx, dims)
      buildNCVar = createNetcdfVariable(ds, buildR, 'buildings_2d', 0, 'm', 'f4', ('y','x'), False, False, fill_value=-9999.9, verbose=False)
      buildNCVar.long_name= "building_height"
      buildNCVar.lod = int(buildLOD)
      return buildNCVar

  elif(buildLOD==2):
    # Save as a 3D boolean mask array

    # I'm quite not sure why axes swapping has to be done but at least it works
    buildR = np.swapaxes(buildR,0,2)
    if('buildings_3d' in vars):
      ds.variables['buildings_3d'][:]=buildR
      return ds.variables['buildings_3d']
    else:
      x_dim = createXDim(ds, buildNPx, buildDPx, dims)
      y_dim = createYDim(ds, buildNPx, buildDPx, dims)
      z_dim = createZDim(ds, buildNPx, buildDPx, dims)
      buildNCVar = createNetcdfVariable(ds, buildR, 'buildings_3d', 0, 'm', 'b', ('z','y','x'), False, False, fill_value=-127, verbose=False)
      buildNCVar.long_name= "building_flag"
      buildNCVar.lod = int(buildLOD)
      return buildNCVar
  else:
    raise ValueError("invalid number of dimensions in buildings array: {}".format(buildLOD+1))

#=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*

def processBuildingIDs(fname,ds,vars,dims):
  buildIDDict = readNumpyZTile(fname,verbose=False)
  buildIDR = buildIDDict['R']
  buildIDDPx = buildIDDict['dPx']
  buildIDNPx = np.shape(buildIDR)

  if('building_id' in vars):
    ds.variables['building_id'][:]=buildIDR
    return ds.variables['building_id']
  else:
    x_dim = createXDim(ds, buildIDNPx, buildIDDPx, dims)
    y_dim = createYDim(ds, buildIDNPx, buildIDDPx, dims)

    buildIDNCVar = createNetcdfVariable(ds, buildIDR, 'building_id', 0, 'm', 'i4', ('y','x'), False, False, fill_value=-9999, verbose=False)
    buildIDNCVar.long_name= "building id numbers"

    return buildIDNCVar

#=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*

def processPavementType(fname,ds,vars,dims):
  pavementTypeDict = readNumpyZTile(fname,verbose=False)
  pavementTypeR = pavementTypeDict['R']
  pavementTypeDPx = pavementTypeDict['dPx']
  pavementTypeNPx = np.shape(pavementTypeR)

  if('pavement_type' in vars):
    ds.variables['pavement_type'][:]=pavementTypeR
    return ds.variables['pavement_type']
  else:
    x_dim = createXDim(ds, pavementTypeNPx, pavementTypeDPx, dims)
    y_dim = createYDim(ds, pavementTypeNPx, pavementTypeDPx, dims)

    pavementTypeNCVar = createNetcdfVariable(ds, pavementTypeR, 'pavement_type', 0, 'm', 'i4', ('y','x'), False, False, fill_value=-9999, verbose=False)
    pavementTypeNCVar.long_name= "pavement type classification"

    return pavementTypeNCVar

#=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*

def processLAD(fname,ds,vars,dims):
  ladDict = readNumpyZTile(fname,verbose=False)
  ladR = ladDict['R']
  ladDPx = ladDict['dPx']
  ladNPx = np.shape(ladR)

  # Same here as in buildings_3d, idk why this has to be done for 3D arrays
  ladR = np.swapaxes(ladR,0,2)

  if('lad' in vars):
    ds.variables['lad'][:]=ladR
    return ds.variables['lad']
  else:
    x_dim = createXDim(ds, ladNPx, ladDPx, dims)
    y_dim = createYDim(ds, ladNPx, ladDPx, dims)
    zlad_dim = createZLADDim(ds, ladNPx, ladDPx, dims)

    ladNCVar = createNetcdfVariable(ds, ladR, 'lad', 0, 'm', 'f4', ('z','y','x'), False, False, fill_value=-9999.9, verbose=False)
    ladNCVar.long_name= "leaf area density"

    return ladNCVar

#=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*

def processVegetationType(fname,ds,vars,dims):
  vegetationTypeDict = readNumpyZTile(fname,verbose=False)
  vegetationTypeR = vegetationTypeDict['R']
  vegetationTypeDPx = vegetationTypeDict['dPx']
  vegetationTypeNPx = np.shape(vegetationTypeR)

  if('vegetation_type' in vars):
    ds.variables['vegetation_type'][:]=vegetationTypeR
    return ds.variables['vegetation_type']
  else:
    x_dim = createXDim(ds, vegetationTypeNPx, vegetationTypeDPx, dims)
    y_dim = createYDim(ds, vegetationTypeNPx, vegetationTypeDPx, dims)

    vegetationTypeNCVar = createNetcdfVariable(ds, vegetationTypeR, 'vegetation_type', 0, 'm', 'i4', ('y','x'), False, False, fill_value=-9999, verbose=False)
    vegetationTypeNCVar.long_name= "vegetation type classification"

    return vegetationTypeNCVar

#=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
#                    PIDS_AERO                      #
#=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*

def createNcatDim(ds, ncat, dims):
  # Creates a new ncat dim unless it already exists
  if('ncat' not in dims):
    ncat_dim = createNetcdfVariable( ds, ncat, 'ncat', len(ncat), '', 'i4', ('ncat',), parameter=True, verbose=False )
    ncat_dim.long_name = "number of emission categories"
    dims.append('ncat')
    return ncat_dim
  else:
    ncat_dim = ds.variables['ncat']
    return ncat_dim

#=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*

def createNspeciesDim(ds, nspecies, dims):
  # Creates a new nspecies dim unless it already exists
  if('nspecies' not in dims):
    nspecies_dim = createNetcdfVariable( ds, nspecies, 'nspecies', len(nspecies), '', 'i4', ('nspecies',), parameter=True, verbose=False )
    nspecies_dim.long_name = "number of emission species"
    dims.append('nspecies')
    return nspecies_dim
  else:
    nspecies_dim = ds.variables['nspecies']
    return nspecies_dim

#=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*

def createCompositionIndexDim(ds, composition_index, dims):
  # Creates a new composition_index dim unless it already exists
  if('composition_index' not in dims):
    composition_index_dim = createNetcdfVariable( ds, composition_index, 'composition_index', len(composition_index), '', 'i4', ('composition_index',), parameter=True, verbose=False )
    composition_index_dim.long_name = "aerosol composition index"
    dims.append('composition_index')
    return composition_index_dim
  else:
    composition_index_dim = ds.variables['composition_index']
    return composition_index_dim

#=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*

def createStrlenDim(ds, strlen, dims):
  # Creates a new strlen dim unless it already exists
  if('strlen' not in dims):
    strlen_dim = createNetcdfVariable( ds, strlen, 'strlen', len(strlen), '', 'i4', ('strlen',), parameter=True, verbose=False )
    dims.append('strlen')
    return strlen_dim
  else:
    strlen_dim = ds.variables['strlen']
    return strlen_dim

#=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*

def createNhoursyearDim(ds, nhoursyear, dims):
  # Creates a new nhoursyear dim unless it already exists
  if('nhoursyear' not in dims):
    nhoursyear_dim = createNetcdfVariable( ds, nhoursyear, 'nhoursyear', len(nhoursyear), '', 'i4', ('nhoursyear',), parameter=True, verbose=False )
    dims.append('nhoursyear')
    return nhoursyear_dim
  else:
    nhoursyear_dim = ds.variables['nhoursyear']
    return nhoursyear_dim

#=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*

def processEmissionCategoryIndices(emiCatInds,ds,vars,dims):
  # In my opinion ncat is completely redundant parameter, emission_category_index should
  # be a coordinate variable with a length of ncat instead. Current setup in PALM doesn't
  # make any sense.
  try:
    emiCatInds=map(int, emiCatInds.split(","))
  except TypeError:
    print("Error: invalid value for emission_category_index in configuration file, expected a comma-delimited list")
    exit(1)
  if('emission_category_index' in vars):
    ds.variables['emission_category_index'][:]=emiCatInds
    return ds.variables['emission_category_index']
  else:
    ncat_dim = createNcatDim(ds, np.arange(1,len(emiCatInds)+1), dims)
    emiCatIndsVar = createNetcdfVariable( ds, emiCatInds, 'emission_category_index', 0, '', 'i1', ('ncat',), parameter=False, verbose=False )
    emiCatIndsVar.long_name = "emission category index"
    emiCatIndsVar.standard_name = 'emission_cat_index'

    return emiCatIndsVar

#=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*

def processEmissionIndices(emiInds,ds,vars,dims):
  # Again, nspecies is redundant
  try:
    emiInds=map(int, emiInds.split(","))
  except TypeError:
    print("Error: invalid value for emission_index in configuration file, expected a comma delimited list")
    exit(1)
  if('emission_index' in vars):
    ds.variables['emission_index'][:]=emiInds
    return ds.variables['emission_index']
  else:
    nspecies_dim = createNspeciesDim(ds, np.arange(1,len(emiInds)+1), dims)
    emiIndsVar = createNetcdfVariable( ds, emiInds, 'emission_index', 0, '', 'u2', ('nspecies',), parameter=False, verbose=False )
    emiIndsVar.long_name = "emission species index"
    emiIndsVar.standard_name = 'emission_index'

    return emiIndsVar

#=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*

def processEmissionCategoryNames(emiCatName,ds,vars,dims):
  try:
    # Max string length is chosen quite arbitralily here
    maxstrlen=10
    emiCatName = parseCharacterArray(emiCatName, maxstrlen)
  except TypeError:
    print("Error: invalid value for emission_category_name in configuration file, expected a comma delimited array")
    exit(1)
  if('emission_category_name' in vars):
    ds.variables['emission_category_name'][:]=emiCatName
    return ds.variables['emission_category_name']
  else:
    ncat_dim = createNcatDim(ds, np.arange(1,np.shape(emiCatName)[0]+1), dims)
    strlen_dim = createStrlenDim(ds, np.arange(1,maxstrlen+1), dims)
    emiCatNameVar = createNetcdfVariable( ds, np.array(emiCatName), 'emission_category_name', 0, '', 'S1', ('ncat','strlen',), parameter=False, verbose=False )
    emiCatNameVar.long_name = "emission category name"
    emiCatNameVar.standard_name = 'emission_cat_name'

    return emiCatNameVar

#=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*

def processEmissionSpeciesNames(emiSpeName,ds,vars,dims):
  try:
    # Max string length is chosen quite arbitralily here
    maxstrlen=10
    emiSpeName = parseCharacterArray(emiSpeName, maxstrlen)
  except TypeError:
    print("Error: invalid value for emission_category_name in configuration file, expected a comma delimited array")
    exit(1)
  if('emission_species_name' in vars):
    ds.variables['emission_species_name'][:]=emiSpeName
    return ds.variables['emission_species_name']
  else:
    nspecies_dim = createNspeciesDim(ds, np.arange(1,np.shape(emiSpeName)[0]+1), dims)
    strlen_dim = createStrlenDim(ds, np.arange(1,maxstrlen+1), dims)

    emiSpeNameVar = createNetcdfVariable( ds, np.array(emiSpeName), 'emission_species_name', 0, '', 'S1', ('nspecies','strlen',), parameter=False, verbose=False )
    emiSpeNameVar.long_name = "emission species name"
    emiSpeNameVar.standard_name = 'emission_name'

    return emiSpeNameVar

#=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*

def processEmissionTimeFactors(emiTimeFactors, lod, ds, vars, dims):
  # Check the level of detail
  if(lod is None or lod=='2'):
    # Using constant value for every hour of year or read factors from npz array
    nhoursyear = np.arange(1,8760+1) # 24*365
    try:
      factor=float(emiTimeFactors)
      if('ncat' in dims):
        ncat=len(ds.variables['ncat'][:])
      else:
        ncat=1
        ncat_dim = createNcatDim(ds, [ncat], dims)
      emiTimeFactors = np.zeros([ncat,len(nhoursyear)],dtype=float)+factor
    except ValueError:
      if(lod is None):
        raise ValueError("emission_time_factors_lod must be set for non-constant emission_time_factors")
      # Try to read 'emission_time_factors' array from given npz file
      try:
        npzDS = np.load(emiTimeFactors)
        emiTimeFactors = npzDS['emission_time_factors']
      except:
        print("Cannot read emission_time_factors data from file \"{}\"".format(emiTimeFactors))
        exit(1)
      if(np.shape(emiTimeFactors)[-1]!=8760):
        raise ValueError("emission_time_factors data must contain exactly 8760 datapoints for every emission category when emission_time_factors_lod = 2")
      ncat_dim = createNcatDim(ds, np.arange(1,np.shape(emiTimeFactors)[0]+1), dims)

    if('emission_time_factors' in vars):
      ds.variables['emission_time_factors'][:] = emiTimeFactors
      return ds.variables['emission_time_factors']
    else:
      nhourstear_dim = createNhoursyearDim(ds, nhoursyear, dims)
      emiTimeFactorsVar = createNetcdfVariable( ds, emiTimeFactors, 'emission_time_factors', 0, '', 'f4', ('ncat','nhoursyear',), parameter=False, verbose=False )
      emiTimeFactorsVar.long_name = "emission time scaling factors"
      emiTimeFactorsVar.standard_name = "emission_time_scaling_factors"

      return emiTimeFactorsVar

  elif(lod=='1'):
    # TODO
    raise NotImplementedError("emission_time_factors_lod = 1 is not yet implemented")
  else:
    raise ValueError("invalid value for emission_time_factors_lod: {}".format(lod))


#=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*

def processCompositionAerosol(compAero,ds,vars,dims):
  try:
    compAero = parseStringArrayInput(compAero, float)
  except TypeError:
    print("Error: invalid value for composition_aerosol in configuration file, expected a newline and comma delimited matrix")
    exit(1)
  if('composition_aerosol' in vars):
    ds.variables['composition_aerosol'][:]=compAero
    return ds.variables['composition_aerosol']
  else:
    ncat_dim = createNcatDim(ds, np.arange(1,np.shape(compAero)[0]+1), dims)
    composition_index_dim = createCompositionIndexDim(ds, np.arange(1,np.shape(compAero)[1]+1), dims)
    compAeroVar = createNetcdfVariable( ds, compAero, 'composition_aerosol', 0, '', 'f4', ('ncat','composition_index',), parameter=False, verbose=False )
    compAeroVar.long_name = "composition aerosol"
    compAeroVar.standard_name = 'composition_aerosol'

    return compAeroVar

#=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*