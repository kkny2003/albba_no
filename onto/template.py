# -*- coding: utf-8 -*-
"""
Created on Wed Jul  9 00:19:21 2025

@author: BSY
"""

from owlready2 import *

onto = get_ontology("http://example.org/bom.owl")

with onto:
    # 1. 클래스 정의
    # Module 클래스
    class Module(Thing): pass

    # EBoM 클래스
    class EBoM(Thing): pass # 품명(Parts, Processes)의 인스턴스들과 중복
    class Level(Thing): pass

    # MBoM 클래스와 서브클래스(포함 안된 서브클래스:품목ID, 동일품목 공정 우선순위)
    class MBoM(Thing): pass
    class Quantity(MBoM): pass # 수량(Parts)
    class Material(MBoM): pass # 재질(Parts, Processes)
    class ProcessType(MBoM): pass # 공정 종류(Parts)
    class ProcessDetail(MBoM): pass # 공정상세(Parts, Processes)
    class ProcessingTime(MBoM): pass # 작업시간(Parts)
    class Cost(MBoM): pass # 비용(Parts)
    class CarbonFootprint(MBoM): pass # 탄소발자국(Parts)
    class ProcessID(MBoM): pass # 공정ID, 선행공정(N/A도 인스턴스) (Processes)

    # Simulation 클래스와 서브클래스
    class Simulation(Thing): pass    
    class Component(Simulation): pass
    class Machine(Component): pass
    class Storage(Component): pass
    class Connection(Simulation): pass

    #2 오브젝트 프로퍼티 정의
    # E-BOM
    class hasChildren(ObjectProperty):  # hasHierarchy --> hasChildren으로 변경
        domain = [EBoM]
        range = [EBoM]
    
    class hasLevel(ObjectProperty):
        domain = [EBoM]
        range = [Level]
    
    # M-BOM
    # Processes - 공정종류
    class hasProcessType(ObjectProperty): # ( processtype -> hasProcessType로 수정 )
        domain = [ProcessID]
        range = [ProcessType]
        
    # 공정 상세(아직 x)
    
    # Processes - 재질
    class hasMaterial(ObjectProperty):  # ( material -> hasMaterial로 수정 )
        domain = [ProcessID]
        range = [Material]
        
     # Processes - 품명        
    class hasProductName(ObjectProperty): # ( productname -> hasProductName로 수정 )
        domain = [ProcessID]
        range = [EBoM]  
        
    # 품목 ID(아직 x)
    
    # Processes - 선행 공정
    class hasPrecedingProcess(ObjectProperty): # ( precedingprocess -> hasPrecedingProcess로 수정 )
        domain = [ProcessID]
        range = [ProcessID]
        
    # 동일품목 공정 우선순위
    
    # Processes - 대상 컴포넌트 목록
    class hasComponents(ObjectProperty): # ( components -> hasComponents로 수정 )
        domain = [ProcessID]
        range = [EBoM]

    # Parts - 수량        
    class hasQuantity(ObjectProperty): # ( quantity -> hasQuantity로 수정 )
        domain = [EBoM]
        range = [Quantity]
        
    # Parts - 작업시간
    class hasProcessingTime(ObjectProperty): # ( processingtime -> hasProcessingTime로 수정 )
        domain = [EBoM]
        range = [ProcessingTime]
    
    # Parts - 비용
    class hasCost(ObjectProperty): # ( cost -> hasCost로 수정)
        domain = [EBoM]
        range = [Cost]
        
    # Parts - 탄소발자국        
    class hasCarbonFootprint(ObjectProperty): # ( carbonfootprint -> hasCarbonFootprint로 수정 )
        domain = [EBoM]
        range = [CarbonFootprint]

    # 시뮬레이션 클래스를 위한 Object Properties
    class result(ObjectProperty):
        domain = [ProcessID]
        range = [EBoM]
        
    class connectedTo(ObjectProperty):
        domain = [Component]
        range = [Component]

    class hasCarbonFootprintSim(ObjectProperty):  # ( hasCarbonFootprint -> hasCarbonFootprintSim으로 수정 )
        domain = [Machine]
        range = [CarbonFootprint]

    class hasCostSim(ObjectProperty): # ( hasCost -> hasCostSim 으로 수정 )
        domain = [Machine]
        range = [Cost]

    class hasInput(ObjectProperty):
        domain = [Component]
        range = [EBoM, Material]

    class hasInputQuantity(ObjectProperty):
        domain = [Machine]
        range = [Quantity]

    class hasOutput(ObjectProperty):
        domain = [Component]
        range = [EBoM, Material]

    class hasOutputQuantity(ObjectProperty):
        domain = [Machine]
        range = [Quantity]

    class hasProcessingTimeSim(ObjectProperty): # ( hasProcessingTime -> hasProcessingTimeSim로 수정)
        domain = [Machine]
        range = [ProcessingTime]

    class isMachineOf(ObjectProperty):
        domain = [Machine]
        range = [ProcessID]

    class isStorageOf(ObjectProperty):
        domain = [Storage]
        range = [EBoM, Material]

    class hasProcessTypeSim(ObjectProperty): 
        domain = [Machine]
        range = [ProcessType]
        
    
    


