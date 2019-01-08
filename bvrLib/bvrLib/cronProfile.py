#   cron profile class definitions. 
#   cron profile implements everything in need of managing the crontab entries for 
#   specific miners. In general, group or subset of miners or all miners in the domain
#   can be assigned to specific cron profile. Each cron profile class instance can be 
#   customized to configure specific cron behavior for the profile thus any miners
#   assigned to that profile. 

class cronProfile:
    dummy = None

    def __init__(self, pAttrib):
        dummy =  0

    def dummy(self):
        dummy = 0
        return None
