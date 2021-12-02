from amt_config import * 

config = AmtConfiguration("amt_defaultconfig.yaml")
config.add("amt_config.yaml")
config.add("amt_schedule.yaml")
config.add("amt_sschedule.yaml")
config.dump()
