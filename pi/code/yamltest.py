from amt_config import * 

config = AmtConfiguration("amt_defaultconfig.yaml")
config.add("amt_config.yaml")
config.add("amt_schedule.yaml")
config.add("amt_sschedule.yaml")
config.set("collectedBy", "Donald Hobern", SECTION_EVENT)
config.set("identifiedBy", [ "Donald Hobern", "iNaturalist"], SECTION_EVENT, "identification")

print("Weight: " + str(config.get("Weight", SECTION_PROVENANCE)))
print("Unit name: " + str(config.get("unitname", SECTION_PROVENANCE, "capture")))
print("Identified by: " + str(config.get("identifiedBy", SECTION_EVENT, "identification")))

config.dump("amt_combined.yaml")
