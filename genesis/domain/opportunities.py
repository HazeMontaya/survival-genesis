from dataclasses import dataclass
@dataclass(frozen=True)
class Opportunity:
 name:str;channel:str;startup_cost_eur:float;expected_margin_eur:float;time_hours:float;confidence:float;repeatability:float=.5
 def score(self):return self.expected_margin_eur*self.confidence*(.5+self.repeatability)/(max(self.startup_cost_eur,.01)*max(self.time_hours,.25))
def rank(x):return sorted(x,key=lambda o:o.score(),reverse=True)
DEFAULT_OPPORTUNITIES=[Opportunity("technical_microservice","service",0,120,3,.45,.65),Opportunity("digital_microproduct","digital_product",0,49,4,.35,.85),Opportunity("lead_generation","leads",0,100,4,.30,.75),Opportunity("open_source_sponsorship","open_source",0,25,2,.15,.90),Opportunity("affiliate_content","affiliate",0,60,5,.20,.70),Opportunity("print_on_demand","pod",0,35,5,.15,.55)]
