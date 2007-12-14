/**********************************************
 *                                            *
 *           Giuseppe Roselli                 *
 *         INFN, Sezione di Bari              *
 *      Via Amendola 173, 70126 Bari          *
 *         Phone: +390805443218               *
 *      giuseppe.roselli@ba.infn.it           *
 *                                            *
 *                                            *
 **********************************************/

#include <stdio.h>
#include <stdlib.h>
#include <iostream>
#include <string>
#include <map>


#include <DataFormats/MuonDetId/interface/RPCDetId.h>
#include "DQM/RPCMonitorDigi/interface/RPCEfficiencyFromTrack.h"

std::map<std::string, MonitorElement*> RPCEfficiencyFromTrack::bookDetUnitTrackEff(RPCDetId & detId) {
  
  std::map<std::string, MonitorElement*> meMap;
  std::string regionName;
  std::string ringType;
  if(detId.region()==0) {
    regionName="Barrel";
    ringType="Wheel";
  }
  else{
    ringType="Disk";
    if(detId.region() == -1) regionName="Endcap-";
    if(detId.region() ==  1) regionName="Endcap+";
  }
  
  char  folder[120];
  sprintf(folder,"RPC/EfficiencyFromTrack/%s/%s_%d/station_%d/sector_%d",regionName.c_str(),ringType.c_str(),
	  detId.ring(),detId.station(),detId.sector());

  dbe->setCurrentFolder(folder);

  char detUnitLabel[128];
  char layerLabel[128];
  sprintf(detUnitLabel ,"%d",detId());
  sprintf(layerLabel ,"layer%d_subsector%d_roll%d",detId.layer(),detId.subsector(),detId.roll());
  
  char meId [128];
  char meTitle [128];
  
  //Begin booking
  sprintf(meId,"ExpectedOccupancyFromTrack_%s",detUnitLabel);
  sprintf(meTitle,"ExpectedOccupancyFromTrack_for_%s",layerLabel);
  meMap[meId] = dbe->book1D(meId, meTitle, 100, 0.5, 100.5);

  sprintf(meId,"RealDetectedOccupancy_%s",detUnitLabel);
  sprintf(meTitle,"RealDetectedOccupancy_for_%s",layerLabel);
  meMap[meId] = dbe->book1D(meId, meTitle, 100, 0.5, 100.5);

  sprintf(meId,"RPCDataOccupancy_%s",detUnitLabel);
  sprintf(meTitle,"RPCDataOccupancy_for_%s",layerLabel);
  meMap[meId] = dbe->book1D(meId, meTitle, 100, 0.5, 100.5);
  
  sprintf(meId,"Residuals_%s",detUnitLabel);
  sprintf(meTitle,"Residuals_for_%s",layerLabel);
  meMap[meId] = dbe->book1D(meId, meTitle, 100,-49.5, 49.);

  sprintf(meId,"Residuals_VS_RecPt_%s",detUnitLabel);
  sprintf(meTitle,"Residuals_VS_RecPt_for_%s",layerLabel);
  meMap[meId] = dbe->book2D(meId, meTitle, 100, 0.5, 100.5,100,-49.5,49.5);

  sprintf(meId,"EfficienyFromTrackExtrapolation_%s",detUnitLabel);
  sprintf(meTitle,"EfficienyFromTrackExtrapolation_for_%s",layerLabel);
  meMap[meId] = dbe->book1D(meId, meTitle, 100, 0.5, 100.5);

  return meMap;
}
