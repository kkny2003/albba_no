# 냉장고 제조공정 시뮬레이션 로그

**시뮬레이션 실행 시간**: 2025년 08월 06일 04시 56분 24초

## 시뮬레이션 출력 로그

```
냉장고 제조 시나리오 생성 중...
[시간 0.0] 고급 자원 등록 (우선순위 지원): transport (용량: 15, 타입: ResourceType.TRANSPORT)
[도어패널 제조] 공정 초기화 완료 - 기계: M001 / 작업자: W001
[도어패널 제조] 한번 실행당 생산량: 1개
[도어패널 제조] Transport 설정 - 자동 운송: 활성화
[도어프레임 제조] 공정 초기화 완료 - 기계: M002 / 작업자: W001
[도어프레임 제조] 한번 실행당 생산량: 1개
[도어프레임 제조] Transport 설정 - 자동 운송: 활성화
[도어 어셈블리] 공정 초기화 완료 - 기계: M003 / 작업자: W002
[도어 어셈블리] 한번 실행당 생산량: 1개
[도어 어셈블리] Transport 설정 - 자동 운송: 활성화
[본체패널 제조] 공정 초기화 완료 - 기계: M004 / 작업자: W003
[본체패널 제조] 한번 실행당 생산량: 1개
[본체패널 제조] Transport 설정 - 자동 운송: 활성화
[본체프레임 제조] 공정 초기화 완료 - 기계: M005 / 작업자: W003
[본체프레임 제조] 한번 실행당 생산량: 1개
[본체프레임 제조] Transport 설정 - 자동 운송: 활성화
[본체 어셈블리] 공정 초기화 완료 - 기계: M006 / 작업자: W004
[본체 어셈블리] 한번 실행당 생산량: 1개
[본체 어셈블리] Transport 설정 - 자동 운송: 활성화
[컴프레서 테스트] 공정 초기화 완료 - 기계: M007 / 작업자: W005
[컴프레서 테스트] 한번 실행당 생산량: 1개
[컴프레서 테스트] Transport 설정 - 자동 운송: 활성화
[가스켓 성형] 공정 초기화 완료 - 기계: M008 / 작업자: W005
[가스켓 성형] 한번 실행당 생산량: 1개
[가스켓 성형] Transport 설정 - 자동 운송: 활성화
[핸들 조립] 공정 초기화 완료 - 기계: M009 / 작업자: W005
[핸들 조립] 한번 실행당 생산량: 1개
[핸들 조립] Transport 설정 - 자동 운송: 활성화
[냉장고 조립] 공정 초기화 완료 - 기계: M010 / 작업자: W006
[냉장고 조립] 한번 실행당 생산량: 1개
[냉장고 조립] Transport 설정 - 자동 운송: 활성화
[품질검사] 공정 초기화 완료 - 기계: M011 / 작업자: W006
[품질검사] 한번 실행당 생산량: 1개
[포장] 공정 초기화 완료 - 기계: M012 / 작업자: W006
[포장] 한번 실행당 생산량: 1개
[포장] Transport 설정 - 자동 운송: 활성화
[도어패널 운송] 공정 초기화 완료 - 기계: T001 / 작업자: W007
[도어패널 운송] 한번 실행당 생산량: 1개
[도어프레임 운송] 공정 초기화 완료 - 기계: T002 / 작업자: W007
[도어프레임 운송] 한번 실행당 생산량: 1개
[본체패널 운송] 공정 초기화 완료 - 기계: T003 / 작업자: W007
[본체패널 운송] 한번 실행당 생산량: 1개
[본체프레임 운송] 공정 초기화 완료 - 기계: T004 / 작업자: W007
[본체프레임 운송] 한번 실행당 생산량: 1개
[최종조립 운송] 공정 초기화 완료 - 기계: T001 / 작업자: W007
[최종조립 운송] 한번 실행당 생산량: 1개
[시간 0.0] TransportProcess 등록: transport_001 (프로세스 ID: DOOR_TRANS_1)
[시간 0.0] TransportProcess 등록: transport_002 (프로세스 ID: DOOR_TRANS_2)
[시간 0.0] TransportProcess 등록: transport_003 (프로세스 ID: BODY_TRANS_1)
[시간 0.0] TransportProcess 등록: transport_004 (프로세스 ID: BODY_TRANS_2)
[시간 0.0] TransportProcess 등록: transport_005 (프로세스 ID: FINAL_TRANS)
냉장고 제조 워크플로우 생성 중...
[그룹래퍼([도어패널 제조 & 도어프레임 제조])] 공정 초기화 완료 - 
[그룹래퍼([도어패널 제조 & 도어프레임 제조])] 한번 실행당 생산량: 1개
[그룹래퍼([본체패널 제조 & 본체프레임 제조])] 공정 초기화 완료 - 
[그룹래퍼([본체패널 제조 & 본체프레임 제조])] 한번 실행당 생산량: 1개
[그룹래퍼([[컴프레서 테스트 & 가스켓 성형 & 핸들 조립] & 그룹래퍼([도어패널 제조 & 도어프레임 제조]) → 도어패널 운송 → 도어프레임 운송 → 도어 어셈블리 & 그룹래퍼([본체패널 제조 & 본체프레임 제조]) → 본체패널 운송 → 본체프레임 운송 → 본체 어셈블리])] 공정 초기화 완료 - 
[그룹래퍼([[컴프레서 테스트 & 가스켓 성형 & 핸들 조립] & 그룹래퍼([도어패널 제조 & 도어프레임 제조]) → 도어패널 운송 → 도어프레임 운송 → 도어 어셈블리 & 그룹래퍼([본체패널 제조 & 본체프레임 제조]) → 본체패널 운송 → 본체프레임 운송 → 본체 어셈블리])] 한번 실행당 생산량: 1개
모니터링 시작...
냉장고 제조 시뮬레이션 실행 중...
=== 냉장고 제조공정 시뮬레이션 시작 ===

=== 시간 0.0 - 냉장고 제조 시스템 상태 ===
기계 상태:
  M001: 사용중=False, 처리수=0
  M002: 사용중=False, 처리수=0
  M003: 사용중=False, 처리수=0
  M004: 사용중=False, 처리수=0
  M005: 사용중=False, 처리수=0
  M006: 사용중=False, 처리수=0
  M007: 사용중=False, 처리수=0
  M008: 사용중=False, 처리수=0
  M009: 사용중=False, 처리수=0
  M010: 사용중=False, 처리수=0
  M011: 사용중=False, 처리수=0
  M012: 사용중=False, 처리수=0
운송수단 상태:
  T001: 적재량 0/5
  T002: 적재량 0/15
  T003: 적재량 0/2
  T004: 적재량 0/3
Transport 관리 상태: 등록된 운송=5

=== 냉장고 1 제조 시작 ===
[시간 0.0] 공정 체인 실행 시작 (체인 ID: 226fae71-c802-4e52-8ed7-50368928922c)
총 5개의 공정을 순차 실행합니다.

[시간 0.0] [1/5] 그룹래퍼([[컴프레서 테스트 & 가스켓 성형 & 핸들 조립] & 그룹래퍼([도어패널 제조 & 도어프레임 제조]) → 도어패널 운송 → 도어프레임 운송 → 도어 어셈블리 & 그룹래퍼([본체패널 제조 & 본체프레임 제조]) → 본체패널 운송 → 본체프레임 운송 → 본체 어셈블리]) 실행 중...
[시간 0.0] 그룹래퍼([[컴프레서 테스트 & 가스켓 성형 & 핸들 조립] & 그룹래퍼([도어패널 제조 & 도어프레임 제조]) → 도어패널 운송 → 도어프레임 운송 → 도어 어셈블리 & 그룹래퍼([본체패널 제조 & 본체프레임 제조]) → 본체패널 운송 → 본체프레임 운송 → 본체 어셈블리]) 실행 시작
[시간 0.0] 다중공정 그룹 실행 시작 (그룹 ID: 7cf81a78-0506-46ef-a529-b14bdd88d425)
순차 실행할 공정: [컴프레서 테스트 & 가스켓 성형 & 핸들 조립], 그룹래퍼([도어패널 제조 & 도어프레임 제조]) → 도어패널 운송 → 도어프레임 운송 → 도어 어셈블리, 그룹래퍼([본체패널 제조 & 본체프레임 제조]) → 본체패널 운송 → 본체프레임 운송 → 본체 어셈블리
  [시간 0.0] [1/3] [컴프레서 테스트 & 가스켓 성형 & 핸들 조립] 실행 중...
[시간 0.0] 다중공정 그룹 실행 시작 (그룹 ID: 23f0efaf-5a28-4ed7-9f41-75550dc6258b)
순차 실행할 공정: 컴프레서 테스트, 가스켓 성형, 핸들 조립
  [시간 0.0] [1/3] 컴프레서 테스트 실행 중...
[시간 0.0] 컴프레서 테스트 실행 시작
[시간 0.0] 컴프레서 테스트 제조 로직 시작
[컴프레서 테스트] 필수 자원 부족: 원자재
  [시간 0.0] [ERROR] 컴프레서 테스트 실행 중 오류: 필요한 자원이 부족합니다
  [시간 0.0] [2/3] 가스켓 성형 실행 중...
[시간 0.0] 가스켓 성형 실행 시작
[시간 0.0] 가스켓 성형 제조 로직 시작
[가스켓 성형] 자원 소비 완료
[가스켓 성형] 자원 생산 완료: 1개 (버퍼: 1/1)
[시간 1.0] 가스켓 성형 제조 로직 완료
[시간 1.0] 가스켓 성형 출하품 운송 요청 시작
[시간 1.0] 가스켓 성형 Transport 요청을 ResourceManager에게 전달
[시간 1.0] ResourceManager: GASKET_MOLDING_PROC로부터 운송 요청 접수
[시간 1.0] ResourceManager: 운송 완료 이벤트 생성 (할당 ID: transport_GASKET_MOLDING_PROC_1.0_28b58ec4)
[시간 1.0] 가스켓 성형 Transport 요청 접수됨 - 완료까지 대기
[시간 1.0] 가스켓 성형 출력 버퍼에서 제품 제거 (운송 요청 접수 완료, 남은 개수: 0)
[시간 1.0] ResourceManager: GASKET_MOLDING_PROC 운송 요청 처리 시작 (할당 ID: transport_GASKET_MOLDING_PROC_1.0_28b58ec4)
[시간 1.0] Transport 할당 완료: transport_001 to GASKET_MOLDING_PROC (할당 ID: 7c499f38-5d50-4f62-9f46-e58b58dc0667, 대기시간: 0.0)
[시간 1.0] ResourceManager: GASKET_MOLDING_PROC 운송 할당 성공 (할당 ID: 7c499f38-5d50-4f62-9f46-e58b58dc0667)
[시간 1.0] ResourceManager: 실제 운송 처리는 TransportProcess에서 수행
[시간 1.0] ResourceManager가 TransportProcess 실행 시작: DOOR_TRANS_1 (요청자: GASKET_MOLDING_PROC)
[시간 1.0] 도어패널 운송 운송 로직 시작
[시간 1.0] 도어패널 운송 적재 중... (소요시간: 0.5)
[시간 1.5] 도어패널 운송 ✅ 적재 완료! ResourceManager에게 알림 전송
[시간 1.5] 도어패널 운송 → ResourceManager: 적재 완료 알림 (요청자: GASKET_MOLDING_PROC)
[시간 1.5] ResourceManager: GASKET_MOLDING_PROC 운송 완료 알림 전송 (성공: True)
[시간 1.5] 도어패널 운송 운송 중... (소요시간: 1.5)
[시간 1.5] 가스켓 성형 Transport 완료 알림 수신: {'allocation_id': 'transport_GASKET_MOLDING_PROC_1.0_28b58ec4', 'requester_id': 'GASKET_MOLDING_PROC', 'success': True, 'completion_time': 1.5}
[시간 1.5] 가스켓 성형 Transport 성공적으로 완료
  [시간 1.5] [OK] 가스켓 성형 완료
  [시간 1.5] [3/3] 핸들 조립 실행 중...
[시간 1.5] 핸들 조립 실행 시작
[시간 1.5] 핸들 조립 제조 로직 시작
[핸들 조립] 자원 소비 완료
[시간 3.0] 도어패널 운송 하역 중... (소요시간: 0.5)
[핸들 조립] 자원 생산 완료: 1개 (버퍼: 1/1)
[시간 3.0] 핸들 조립 제조 로직 완료
[시간 3.0] 핸들 조립 출하품 운송 요청 시작
[시간 3.0] 핸들 조립 Transport 요청을 ResourceManager에게 전달
[시간 3.0] ResourceManager: HANDLE_ASSEMBLY_PROC로부터 운송 요청 접수
[시간 3.0] ResourceManager: 운송 완료 이벤트 생성 (할당 ID: transport_HANDLE_ASSEMBLY_PROC_3.0_d556eff7)
[시간 3.0] 핸들 조립 Transport 요청 접수됨 - 완료까지 대기
[시간 3.0] 핸들 조립 출력 버퍼에서 제품 제거 (운송 요청 접수 완료, 남은 개수: 0)
[시간 3.0] ResourceManager: HANDLE_ASSEMBLY_PROC 운송 요청 처리 시작 (할당 ID: transport_HANDLE_ASSEMBLY_PROC_3.0_d556eff7)
[시간 3.0] Transport 할당 완료: transport_001 to HANDLE_ASSEMBLY_PROC (할당 ID: 1d852fd4-a4d3-48cc-b93b-63f759a55832, 대기시간: 0.0)
[시간 3.0] ResourceManager: HANDLE_ASSEMBLY_PROC 운송 할당 성공 (할당 ID: 1d852fd4-a4d3-48cc-b93b-63f759a55832)
[시간 3.0] ResourceManager: 실제 운송 처리는 TransportProcess에서 수행
[시간 3.0] ResourceManager가 TransportProcess 실행 시작: DOOR_TRANS_1 (요청자: HANDLE_ASSEMBLY_PROC)
[시간 3.0] 도어패널 운송 운송 로직 시작
[시간 3.0] 도어패널 운송 적재 중... (소요시간: 0.5)
[시간 3.5] 도어패널 운송 대기 중... (소요시간: 0.3)
[시간 3.5] 도어패널 운송 ✅ 적재 완료! ResourceManager에게 알림 전송
[시간 3.5] 도어패널 운송 → ResourceManager: 적재 완료 알림 (요청자: HANDLE_ASSEMBLY_PROC)
[시간 3.5] ResourceManager: HANDLE_ASSEMBLY_PROC 운송 완료 알림 전송 (성공: True)
[시간 3.5] 도어패널 운송 운송 중... (소요시간: 1.5)
[시간 3.5] 핸들 조립 Transport 완료 알림 수신: {'allocation_id': 'transport_HANDLE_ASSEMBLY_PROC_3.0_d556eff7', 'requester_id': 'HANDLE_ASSEMBLY_PROC', 'success': True, 'completion_time': 3.5}
[시간 3.5] 핸들 조립 Transport 성공적으로 완료
  [시간 3.5] [OK] 핸들 조립 완료
[시간 3.5] 다중공정 그룹 실행 완료 (그룹 ID: 23f0efaf-5a28-4ed7-9f41-75550dc6258b)
  [시간 3.5] [OK] [컴프레서 테스트 & 가스켓 성형 & 핸들 조립] 완료
  [시간 3.5] [2/3] 그룹래퍼([도어패널 제조 & 도어프레임 제조]) → 도어패널 운송 → 도어프레임 운송 → 도어 어셈블리 실행 중...
[시간 3.5] 공정 체인 실행 시작 (체인 ID: f7887c98-8c4b-4c8d-b3df-e1a15cb92d9d)
총 4개의 공정을 순차 실행합니다.

[시간 3.5] [1/4] 그룹래퍼([도어패널 제조 & 도어프레임 제조]) 실행 중...
[시간 3.5] 그룹래퍼([도어패널 제조 & 도어프레임 제조]) 실행 시작
[시간 3.5] 다중공정 그룹 실행 시작 (그룹 ID: 922310b9-ca6e-42eb-89df-0069e3e36932)
순차 실행할 공정: 도어패널 제조, 도어프레임 제조
  [시간 3.5] [1/2] 도어패널 제조 실행 중...
[시간 3.5] 도어패널 제조 실행 시작
[시간 3.5] 도어패널 제조 제조 로직 시작
[도어패널 제조] 자원 소비 완료
[시간 3.8] 도어패널 운송 운송 로직 완료
[시간 3.8] ResourceManager가 TransportProcess 실행 완료: DOOR_TRANS_1
[시간 3.8] ResourceManager: 전체 운송 프로세스 완료 (적재 완료 시 이미 알림 전송됨)
[시간 5.0] 도어패널 운송 하역 중... (소요시간: 0.5)
[도어패널 제조] 자원 생산 완료: 1개 (버퍼: 1/1)
[시간 5.5] 도어패널 제조 제조 로직 완료
[시간 5.5] 도어패널 제조 출하품 운송 요청 시작
[시간 5.5] 도어패널 제조 Transport 요청을 ResourceManager에게 전달
[시간 5.5] ResourceManager: DOOR_PANEL_PROC로부터 운송 요청 접수
[시간 5.5] ResourceManager: 운송 완료 이벤트 생성 (할당 ID: transport_DOOR_PANEL_PROC_5.5_08c9e6ac)
[시간 5.5] 도어패널 제조 Transport 요청 접수됨 - 완료까지 대기
[시간 5.5] 도어패널 제조 출력 버퍼에서 제품 제거 (운송 요청 접수 완료, 남은 개수: 0)
[시간 5.5] ResourceManager: DOOR_PANEL_PROC 운송 요청 처리 시작 (할당 ID: transport_DOOR_PANEL_PROC_5.5_08c9e6ac)
[시간 5.5] 도어패널 운송 대기 중... (소요시간: 0.3)
[시간 5.5] Transport 할당 완료: transport_001 to DOOR_PANEL_PROC (할당 ID: 03f1badf-1fe2-46f2-a405-d3e90d009f89, 대기시간: 0.0)
[시간 5.5] ResourceManager: DOOR_PANEL_PROC 운송 할당 성공 (할당 ID: 03f1badf-1fe2-46f2-a405-d3e90d009f89)
[시간 5.5] ResourceManager: 실제 운송 처리는 TransportProcess에서 수행
[시간 5.5] ResourceManager가 TransportProcess 실행 시작: DOOR_TRANS_1 (요청자: DOOR_PANEL_PROC)
[시간 5.5] 도어패널 운송 운송 로직 시작
[시간 5.5] 도어패널 운송 적재 중... (소요시간: 0.5)
[시간 5.8] 도어패널 운송 운송 로직 완료
[시간 5.8] ResourceManager가 TransportProcess 실행 완료: DOOR_TRANS_1
[시간 5.8] ResourceManager: 전체 운송 프로세스 완료 (적재 완료 시 이미 알림 전송됨)
[시간 6.0] 도어패널 운송 ✅ 적재 완료! ResourceManager에게 알림 전송
[시간 6.0] 도어패널 운송 → ResourceManager: 적재 완료 알림 (요청자: DOOR_PANEL_PROC)
[시간 6.0] ResourceManager: DOOR_PANEL_PROC 운송 완료 알림 전송 (성공: True)
[시간 6.0] 도어패널 운송 운송 중... (소요시간: 1.5)
[시간 6.0] 도어패널 제조 Transport 완료 알림 수신: {'allocation_id': 'transport_DOOR_PANEL_PROC_5.5_08c9e6ac', 'requester_id': 'DOOR_PANEL_PROC', 'success': True, 'completion_time': 6.0}
[시간 6.0] 도어패널 제조 Transport 성공적으로 완료
  [시간 6.0] [OK] 도어패널 제조 완료
  [시간 6.0] [2/2] 도어프레임 제조 실행 중...
[시간 6.0] 도어프레임 제조 실행 시작
[시간 6.0] 도어프레임 제조 제조 로직 시작
[도어프레임 제조] 자원 소비 완료
[시간 7.5] 도어패널 운송 하역 중... (소요시간: 0.5)
[시간 8.0] 도어패널 운송 대기 중... (소요시간: 0.3)
[시간 8.3] 도어패널 운송 운송 로직 완료
[시간 8.3] ResourceManager가 TransportProcess 실행 완료: DOOR_TRANS_1
[시간 8.3] ResourceManager: 전체 운송 프로세스 완료 (적재 완료 시 이미 알림 전송됨)
[도어프레임 제조] 자원 생산 완료: 1개 (버퍼: 1/1)
[시간 8.5] 도어프레임 제조 제조 로직 완료
[시간 8.5] 도어프레임 제조 출하품 운송 요청 시작
[시간 8.5] 도어프레임 제조 Transport 요청을 ResourceManager에게 전달
[시간 8.5] ResourceManager: DOOR_FRAME_PROC로부터 운송 요청 접수
[시간 8.5] ResourceManager: 운송 완료 이벤트 생성 (할당 ID: transport_DOOR_FRAME_PROC_8.5_c2bdeac9)
[시간 8.5] 도어프레임 제조 Transport 요청 접수됨 - 완료까지 대기
[시간 8.5] 도어프레임 제조 출력 버퍼에서 제품 제거 (운송 요청 접수 완료, 남은 개수: 0)
[시간 8.5] ResourceManager: DOOR_FRAME_PROC 운송 요청 처리 시작 (할당 ID: transport_DOOR_FRAME_PROC_8.5_c2bdeac9)
[시간 8.5] Transport 할당 완료: transport_001 to DOOR_FRAME_PROC (할당 ID: ecc8e8fd-0c16-4c40-b601-ab38b706d768, 대기시간: 0.0)
[시간 8.5] ResourceManager: DOOR_FRAME_PROC 운송 할당 성공 (할당 ID: ecc8e8fd-0c16-4c40-b601-ab38b706d768)
[시간 8.5] ResourceManager: 실제 운송 처리는 TransportProcess에서 수행
[시간 8.5] ResourceManager가 TransportProcess 실행 시작: DOOR_TRANS_1 (요청자: DOOR_FRAME_PROC)
[시간 8.5] 도어패널 운송 운송 로직 시작
[시간 8.5] 도어패널 운송 적재 중... (소요시간: 0.5)
[시간 9.0] 도어패널 운송 ✅ 적재 완료! ResourceManager에게 알림 전송
[시간 9.0] 도어패널 운송 → ResourceManager: 적재 완료 알림 (요청자: DOOR_FRAME_PROC)
[시간 9.0] ResourceManager: DOOR_FRAME_PROC 운송 완료 알림 전송 (성공: True)
[시간 9.0] 도어패널 운송 운송 중... (소요시간: 1.5)
[시간 9.0] 도어프레임 제조 Transport 완료 알림 수신: {'allocation_id': 'transport_DOOR_FRAME_PROC_8.5_c2bdeac9', 'requester_id': 'DOOR_FRAME_PROC', 'success': True, 'completion_time': 9.0}
[시간 9.0] 도어프레임 제조 Transport 성공적으로 완료
  [시간 9.0] [OK] 도어프레임 제조 완료
[시간 9.0] 다중공정 그룹 실행 완료 (그룹 ID: 922310b9-ca6e-42eb-89df-0069e3e36932)
[시간 9.0] [1/4] 그룹래퍼([도어패널 제조 & 도어프레임 제조]) 완료

[시간 9.0] [2/4] 도어패널 운송 실행 중...
[시간 9.0] 도어패널 운송 실행 시작
[경고] 기계 1에 operate 메서드가 없습니다.
[시간 9.0] 도어패널 운송 운송 로직 시작
[시간 9.0] 도어패널 운송 적재 중... (소요시간: 0.5)
[시간 9.5] 도어패널 운송 ✅ 적재 완료! ResourceManager에게 알림 전송
[시간 9.5] 도어패널 운송 ⚠️ 적재 완료 알림 생략 (필요한 정보 부족)
[시간 9.5] 도어패널 운송 운송 중... (소요시간: 1.5)
[시간 10.5] 도어패널 운송 하역 중... (소요시간: 0.5)
[시간 11.0] 도어패널 운송 하역 중... (소요시간: 0.5)
[시간 11.0] 도어패널 운송 대기 중... (소요시간: 0.3)
[시간 11.3] 도어패널 운송 운송 로직 완료
[시간 11.3] ResourceManager가 TransportProcess 실행 완료: DOOR_TRANS_1
[시간 11.3] ResourceManager: 전체 운송 프로세스 완료 (적재 완료 시 이미 알림 전송됨)
[시간 11.5] 도어패널 운송 대기 중... (소요시간: 0.3)
[시간 11.8] 도어패널 운송 운송 로직 완료
[시간 11.8] [2/4] 도어패널 운송 완료

[시간 11.8] [3/4] 도어프레임 운송 실행 중...
[시간 11.8] 도어프레임 운송 실행 시작
[경고] 기계 1에 operate 메서드가 없습니다.
[시간 11.8] 도어프레임 운송 운송 로직 시작
[시간 11.8] 도어프레임 운송 적재 중... (소요시간: 0.3)
[시간 12.1] 도어프레임 운송 ✅ 적재 완료! ResourceManager에게 알림 전송
[시간 12.1] 도어프레임 운송 ⚠️ 적재 완료 알림 생략 (필요한 정보 부족)
[시간 12.1] 도어프레임 운송 운송 중... (소요시간: 1.0)
[시간 13.1] 도어프레임 운송 하역 중... (소요시간: 0.3)
[시간 13.4] 도어프레임 운송 대기 중... (소요시간: 0.2)
[시간 13.6] 도어프레임 운송 운송 로직 완료
[시간 13.6] [3/4] 도어프레임 운송 완료

[시간 13.6] [4/4] 도어 어셈블리 실행 중...
[시간 13.6] 도어 어셈블리 실행 시작
[시간 13.6] 도어 어셈블리 조립 로직 시작

=== 시간 15.0 - 냉장고 제조 시스템 상태 ===
기계 상태:
  M001: 사용중=False, 처리수=0
  M002: 사용중=False, 처리수=0
  M003: 사용중=False, 처리수=0
  M004: 사용중=False, 처리수=0
  M005: 사용중=False, 처리수=0
  M006: 사용중=False, 처리수=0
  M007: 사용중=False, 처리수=0
  M008: 사용중=False, 처리수=0
  M009: 사용중=False, 처리수=0
  M010: 사용중=False, 처리수=0
  M011: 사용중=False, 처리수=0
  M012: 사용중=False, 처리수=0
운송수단 상태:
  T001: 적재량 0/5
  T002: 적재량 0/15
  T003: 적재량 0/2
  T004: 적재량 0/3
Transport 관리 상태: 등록된 운송=5
[시간 16.6] 도어 어셈블리 조립 로직 완료
[시간 16.6] 도어 어셈블리 조립품 운송 요청 시작
[시간 16.6] 도어 어셈블리 Transport 요청을 ResourceManager에게 전달
[시간 16.6] ResourceManager: DOOR_ASSEMBLY_PROC로부터 운송 요청 접수
[시간 16.6] ResourceManager: 운송 완료 이벤트 생성 (할당 ID: transport_DOOR_ASSEMBLY_PROC_16.6_dce2dab7)
[시간 16.6] 도어 어셈블리 Transport 요청 접수됨 - 완료까지 대기
[시간 16.6] ResourceManager: DOOR_ASSEMBLY_PROC 운송 요청 처리 시작 (할당 ID: transport_DOOR_ASSEMBLY_PROC_16.6_dce2dab7)
[시간 16.6] Transport 할당 완료: transport_001 to DOOR_ASSEMBLY_PROC (할당 ID: 6552cc99-842e-4826-b1e8-74dea7098d1d, 대기시간: 0.0)
[시간 16.6] ResourceManager: DOOR_ASSEMBLY_PROC 운송 할당 성공 (할당 ID: 6552cc99-842e-4826-b1e8-74dea7098d1d)
[시간 16.6] ResourceManager: 실제 운송 처리는 TransportProcess에서 수행
[시간 16.6] ResourceManager가 TransportProcess 실행 시작: DOOR_TRANS_1 (요청자: DOOR_ASSEMBLY_PROC)
[시간 16.6] 도어패널 운송 운송 로직 시작
[시간 16.6] 도어패널 운송 적재 중... (소요시간: 0.5)
[시간 17.1] 도어패널 운송 ✅ 적재 완료! ResourceManager에게 알림 전송
[시간 17.1] 도어패널 운송 → ResourceManager: 적재 완료 알림 (요청자: DOOR_ASSEMBLY_PROC)
[시간 17.1] ResourceManager: DOOR_ASSEMBLY_PROC 운송 완료 알림 전송 (성공: True)
[시간 17.1] 도어패널 운송 운송 중... (소요시간: 1.5)
[시간 17.1] 도어 어셈블리 Transport 완료 알림 수신: {'allocation_id': 'transport_DOOR_ASSEMBLY_PROC_16.6_dce2dab7', 'requester_id': 'DOOR_ASSEMBLY_PROC', 'success': True, 'completion_time': 17.1}
[시간 17.1] 도어 어셈블리 Transport 성공적으로 완료
[시간 17.1] [4/4] 도어 어셈블리 완료

[시간 17.1] 공정 체인 실행 완료 (체인 ID: f7887c98-8c4b-4c8d-b3df-e1a15cb92d9d)
  [시간 17.1] [OK] 그룹래퍼([도어패널 제조 & 도어프레임 제조]) → 도어패널 운송 → 도어프레임 운송 → 도어 어셈블리 완료
  [시간 17.1] [3/3] 그룹래퍼([본체패널 제조 & 본체프레임 제조]) → 본체패널 운송 → 본체프레임 운송 → 본체 어셈블리 실행 중...
[시간 17.1] 공정 체인 실행 시작 (체인 ID: d5c8e259-10cd-405d-869f-bdd255309459)
총 4개의 공정을 순차 실행합니다.

[시간 17.1] [1/4] 그룹래퍼([본체패널 제조 & 본체프레임 제조]) 실행 중...
[시간 17.1] 그룹래퍼([본체패널 제조 & 본체프레임 제조]) 실행 시작
[시간 17.1] 다중공정 그룹 실행 시작 (그룹 ID: 3d434c58-10b8-46d9-898f-5809c58d9ab1)
순차 실행할 공정: 본체패널 제조, 본체프레임 제조
  [시간 17.1] [1/2] 본체패널 제조 실행 중...
[시간 17.1] 본체패널 제조 실행 시작
[시간 17.1] 본체패널 제조 제조 로직 시작
[본체패널 제조] 필수 자원 부족: 강판
  [시간 17.1] [ERROR] 본체패널 제조 실행 중 오류: 필요한 자원이 부족합니다
  [시간 17.1] [2/2] 본체프레임 제조 실행 중...
[시간 17.1] 본체프레임 제조 실행 시작
[시간 17.1] 본체프레임 제조 제조 로직 시작
[본체프레임 제조] 필수 자원 부족: 강판
  [시간 17.1] [ERROR] 본체프레임 제조 실행 중 오류: 필요한 자원이 부족합니다
[시간 17.1] 다중공정 그룹 실행 완료 (그룹 ID: 3d434c58-10b8-46d9-898f-5809c58d9ab1)
[시간 17.1] [1/4] 그룹래퍼([본체패널 제조 & 본체프레임 제조]) 완료

[시간 17.1] [2/4] 본체패널 운송 실행 중...
[시간 17.1] 본체패널 운송 실행 시작
[경고] 기계 1에 operate 메서드가 없습니다.
[시간 17.1] 본체패널 운송 운송 로직 시작
[시간 17.1] 본체패널 운송 적재 중... (소요시간: 0.4)
[시간 17.5] 본체패널 운송 ✅ 적재 완료! ResourceManager에게 알림 전송
[시간 17.5] 본체패널 운송 ⚠️ 적재 완료 알림 생략 (필요한 정보 부족)
[시간 17.5] 본체패널 운송 운송 중... (소요시간: 1.2)
[시간 18.6] 도어패널 운송 하역 중... (소요시간: 0.5)
[시간 18.7] 본체패널 운송 하역 중... (소요시간: 0.4)
[시간 19.1] 본체패널 운송 대기 중... (소요시간: 0.3)
[시간 19.1] 도어패널 운송 대기 중... (소요시간: 0.3)
[시간 19.4] 본체패널 운송 운송 로직 완료
[시간 19.4] [2/4] 본체패널 운송 완료

[시간 19.4] [3/4] 본체프레임 운송 실행 중...
[시간 19.4] 본체프레임 운송 실행 시작
[경고] 기계 1에 operate 메서드가 없습니다.
[시간 19.4] 본체프레임 운송 운송 로직 시작
[시간 19.4] 본체프레임 운송 적재 중... (소요시간: 0.6)
[시간 19.4] 도어패널 운송 운송 로직 완료
[시간 19.4] ResourceManager가 TransportProcess 실행 완료: DOOR_TRANS_1
[시간 19.4] ResourceManager: 전체 운송 프로세스 완료 (적재 완료 시 이미 알림 전송됨)
[시간 20.0] 본체프레임 운송 ✅ 적재 완료! ResourceManager에게 알림 전송
[시간 20.0] 본체프레임 운송 ⚠️ 적재 완료 알림 생략 (필요한 정보 부족)
[시간 20.0] 본체프레임 운송 운송 중... (소요시간: 2.0)
[시간 22.0] 본체프레임 운송 하역 중... (소요시간: 0.6)
[시간 22.6] 본체프레임 운송 대기 중... (소요시간: 0.4)
[시간 23.0] 본체프레임 운송 운송 로직 완료
[시간 23.0] [3/4] 본체프레임 운송 완료

[시간 23.0] [4/4] 본체 어셈블리 실행 중...
[시간 23.0] 본체 어셈블리 실행 시작
[시간 23.0] 본체 어셈블리 조립 로직 시작
[시간 26.5] 본체 어셈블리 조립 로직 완료
[시간 26.5] 본체 어셈블리 조립품 운송 요청 시작
[시간 26.5] 본체 어셈블리 Transport 요청을 ResourceManager에게 전달
[시간 26.5] ResourceManager: BODY_ASSEMBLY_PROC로부터 운송 요청 접수
[시간 26.5] ResourceManager: 운송 완료 이벤트 생성 (할당 ID: transport_BODY_ASSEMBLY_PROC_26.5_00783c58)
[시간 26.5] 본체 어셈블리 Transport 요청 접수됨 - 완료까지 대기
[시간 26.5] ResourceManager: BODY_ASSEMBLY_PROC 운송 요청 처리 시작 (할당 ID: transport_BODY_ASSEMBLY_PROC_26.5_00783c58)
[시간 26.5] Transport 할당 완료: transport_001 to BODY_ASSEMBLY_PROC (할당 ID: d818cc91-af11-482c-829e-8cd1a8a08219, 대기시간: 0.0)
[시간 26.5] ResourceManager: BODY_ASSEMBLY_PROC 운송 할당 성공 (할당 ID: d818cc91-af11-482c-829e-8cd1a8a08219)
[시간 26.5] ResourceManager: 실제 운송 처리는 TransportProcess에서 수행
[시간 26.5] ResourceManager가 TransportProcess 실행 시작: DOOR_TRANS_1 (요청자: BODY_ASSEMBLY_PROC)
[시간 26.5] 도어패널 운송 운송 로직 시작
[시간 26.5] 도어패널 운송 적재 중... (소요시간: 0.5)
[시간 27.0] 도어패널 운송 ✅ 적재 완료! ResourceManager에게 알림 전송
[시간 27.0] 도어패널 운송 → ResourceManager: 적재 완료 알림 (요청자: BODY_ASSEMBLY_PROC)
[시간 27.0] ResourceManager: BODY_ASSEMBLY_PROC 운송 완료 알림 전송 (성공: True)
[시간 27.0] 도어패널 운송 운송 중... (소요시간: 1.5)
[시간 27.0] 본체 어셈블리 Transport 완료 알림 수신: {'allocation_id': 'transport_BODY_ASSEMBLY_PROC_26.5_00783c58', 'requester_id': 'BODY_ASSEMBLY_PROC', 'success': True, 'completion_time': 27.0}
[시간 27.0] 본체 어셈블리 Transport 성공적으로 완료
[시간 27.0] [4/4] 본체 어셈블리 완료

[시간 27.0] 공정 체인 실행 완료 (체인 ID: d5c8e259-10cd-405d-869f-bdd255309459)
  [시간 27.0] [OK] 그룹래퍼([본체패널 제조 & 본체프레임 제조]) → 본체패널 운송 → 본체프레임 운송 → 본체 어셈블리 완료
[시간 27.0] 다중공정 그룹 실행 완료 (그룹 ID: 7cf81a78-0506-46ef-a529-b14bdd88d425)
[시간 27.0] [1/5] 그룹래퍼([[컴프레서 테스트 & 가스켓 성형 & 핸들 조립] & 그룹래퍼([도어패널 제조 & 도어프레임 제조]) → 도어패널 운송 → 도어프레임 운송 → 도어 어셈블리 & 그룹래퍼([본체패널 제조 & 본체프레임 제조]) → 본체패널 운송 → 본체프레임 운송 → 본체 어셈블리]) 완료

[시간 27.0] [2/5] 최종조립 운송 실행 중...
[시간 27.0] 최종조립 운송 실행 시작
[경고] 기계 1에 operate 메서드가 없습니다.
[시간 27.0] 최종조립 운송 운송 로직 시작
[시간 27.0] 최종조립 운송 적재 중... (소요시간: 1.0)
[시간 28.0] 최종조립 운송 ✅ 적재 완료! ResourceManager에게 알림 전송
[시간 28.0] 최종조립 운송 ⚠️ 적재 완료 알림 생략 (필요한 정보 부족)
[시간 28.0] 최종조립 운송 운송 중... (소요시간: 2.5)
[시간 28.5] 도어패널 운송 하역 중... (소요시간: 0.5)
[시간 29.0] 도어패널 운송 대기 중... (소요시간: 0.3)
[시간 29.3] 도어패널 운송 운송 로직 완료
[시간 29.3] ResourceManager가 TransportProcess 실행 완료: DOOR_TRANS_1
[시간 29.3] ResourceManager: 전체 운송 프로세스 완료 (적재 완료 시 이미 알림 전송됨)

=== 시간 30.0 - 냉장고 제조 시스템 상태 ===
기계 상태:
  M001: 사용중=False, 처리수=0
  M002: 사용중=False, 처리수=0
  M003: 사용중=False, 처리수=0
  M004: 사용중=False, 처리수=0
  M005: 사용중=False, 처리수=0
  M006: 사용중=False, 처리수=0
  M007: 사용중=False, 처리수=0
  M008: 사용중=False, 처리수=0
  M009: 사용중=False, 처리수=0
  M010: 사용중=False, 처리수=0
  M011: 사용중=False, 처리수=0
  M012: 사용중=False, 처리수=0
운송수단 상태:
  T001: 적재량 0/5
  T002: 적재량 0/15
  T003: 적재량 0/2
  T004: 적재량 0/3
Transport 관리 상태: 등록된 운송=5
[시간 30.5] 최종조립 운송 하역 중... (소요시간: 1.0)
[시간 31.5] 최종조립 운송 대기 중... (소요시간: 0.5)
[시간 32.0] 최종조립 운송 운송 로직 완료
[시간 32.0] [2/5] 최종조립 운송 완료

[시간 32.0] [3/5] 냉장고 조립 실행 중...
[시간 32.0] 냉장고 조립 실행 시작
[시간 32.0] 냉장고 조립 조립 로직 시작
[시간 36.0] 냉장고 조립 조립 로직 완료
[시간 36.0] 냉장고 조립 조립품 운송 요청 시작
[시간 36.0] 냉장고 조립 Transport 요청을 ResourceManager에게 전달
[시간 36.0] ResourceManager: REFRIGERATOR_ASSEMBLY_PROC로부터 운송 요청 접수
[시간 36.0] ResourceManager: 운송 완료 이벤트 생성 (할당 ID: transport_REFRIGERATOR_ASSEMBLY_PROC_36.0_bf2f04ee)
[시간 36.0] 냉장고 조립 Transport 요청 접수됨 - 완료까지 대기
[시간 36.0] ResourceManager: REFRIGERATOR_ASSEMBLY_PROC 운송 요청 처리 시작 (할당 ID: transport_REFRIGERATOR_ASSEMBLY_PROC_36.0_bf2f04ee)
[시간 36.0] Transport 할당 완료: transport_001 to REFRIGERATOR_ASSEMBLY_PROC (할당 ID: 85c39aef-459a-4e41-9dcd-06b00338e3b3, 대기시간: 0.0)
[시간 36.0] ResourceManager: REFRIGERATOR_ASSEMBLY_PROC 운송 할당 성공 (할당 ID: 85c39aef-459a-4e41-9dcd-06b00338e3b3)
[시간 36.0] ResourceManager: 실제 운송 처리는 TransportProcess에서 수행
[시간 36.0] ResourceManager가 TransportProcess 실행 시작: DOOR_TRANS_1 (요청자: REFRIGERATOR_ASSEMBLY_PROC)
[시간 36.0] 도어패널 운송 운송 로직 시작
[시간 36.0] 도어패널 운송 적재 중... (소요시간: 0.5)
[시간 36.5] 도어패널 운송 ✅ 적재 완료! ResourceManager에게 알림 전송
[시간 36.5] 도어패널 운송 → ResourceManager: 적재 완료 알림 (요청자: REFRIGERATOR_ASSEMBLY_PROC)
[시간 36.5] ResourceManager: REFRIGERATOR_ASSEMBLY_PROC 운송 완료 알림 전송 (성공: True)
[시간 36.5] 도어패널 운송 운송 중... (소요시간: 1.5)
[시간 36.5] 냉장고 조립 Transport 완료 알림 수신: {'allocation_id': 'transport_REFRIGERATOR_ASSEMBLY_PROC_36.0_bf2f04ee', 'requester_id': 'REFRIGERATOR_ASSEMBLY_PROC', 'success': True, 'completion_time': 36.5}
[시간 36.5] 냉장고 조립 Transport 성공적으로 완료
[시간 36.5] [3/5] 냉장고 조립 완료

[시간 36.5] [4/5] 품질검사 실행 중...
[시간 36.5] 품질검사 실행 시작
[시간 36.5] 품질검사 검사 로직 시작
[시간 38.0] 도어패널 운송 하역 중... (소요시간: 0.5)
[시간 38.5] 품질검사 검사 로직 완료
[시간 38.5] [4/5] 품질검사 완료

[시간 38.5] [5/5] 포장 실행 중...
[시간 38.5] 포장 실행 시작
[시간 38.5] 포장 제조 로직 시작
[포장] 필수 자원 부족: 원자재
[시간 38.5] [5/5] 포장 실행 중 오류: 필요한 자원이 부족합니다
냉장고 1 제조 실패: 필요한 자원이 부족합니다
[시간 38.5] 도어패널 운송 대기 중... (소요시간: 0.3)
[시간 38.8] 도어패널 운송 운송 로직 완료
[시간 38.8] ResourceManager가 TransportProcess 실행 완료: DOOR_TRANS_1
[시간 38.8] ResourceManager: 전체 운송 프로세스 완료 (적재 완료 시 이미 알림 전송됨)

=== 냉장고 2 제조 시작 ===
[시간 41.5] 공정 체인 실행 시작 (체인 ID: 226fae71-c802-4e52-8ed7-50368928922c)
총 5개의 공정을 순차 실행합니다.

[시간 41.5] [1/5] 그룹래퍼([[컴프레서 테스트 & 가스켓 성형 & 핸들 조립] & 그룹래퍼([도어패널 제조 & 도어프레임 제조]) → 도어패널 운송 → 도어프레임 운송 → 도어 어셈블리 & 그룹래퍼([본체패널 제조 & 본체프레임 제조]) → 본체패널 운송 → 본체프레임 운송 → 본체 어셈블리]) 실행 중...
[시간 41.5] 그룹래퍼([[컴프레서 테스트 & 가스켓 성형 & 핸들 조립] & 그룹래퍼([도어패널 제조 & 도어프레임 제조]) → 도어패널 운송 → 도어프레임 운송 → 도어 어셈블리 & 그룹래퍼([본체패널 제조 & 본체프레임 제조]) → 본체패널 운송 → 본체프레임 운송 → 본체 어셈블리]) 실행 시작
[시간 41.5] 다중공정 그룹 실행 시작 (그룹 ID: 7cf81a78-0506-46ef-a529-b14bdd88d425)
순차 실행할 공정: [컴프레서 테스트 & 가스켓 성형 & 핸들 조립], 그룹래퍼([도어패널 제조 & 도어프레임 제조]) → 도어패널 운송 → 도어프레임 운송 → 도어 어셈블리, 그룹래퍼([본체패널 제조 & 본체프레임 제조]) → 본체패널 운송 → 본체프레임 운송 → 본체 어셈블리
  [시간 41.5] [1/3] [컴프레서 테스트 & 가스켓 성형 & 핸들 조립] 실행 중...
[시간 41.5] 다중공정 그룹 실행 시작 (그룹 ID: 23f0efaf-5a28-4ed7-9f41-75550dc6258b)
순차 실행할 공정: 컴프레서 테스트, 가스켓 성형, 핸들 조립
  [시간 41.5] [1/3] 컴프레서 테스트 실행 중...
[시간 41.5] 컴프레서 테스트 실행 시작
[시간 41.5] 컴프레서 테스트 제조 로직 시작
[컴프레서 테스트] 필수 자원 부족: 원자재
  [시간 41.5] [ERROR] 컴프레서 테스트 실행 중 오류: 필요한 자원이 부족합니다
  [시간 41.5] [2/3] 가스켓 성형 실행 중...
[시간 41.5] 가스켓 성형 실행 시작
[시간 41.5] 가스켓 성형 제조 로직 시작
[가스켓 성형] 자원 소비 완료
[가스켓 성형] 자원 생산 완료: 1개 (버퍼: 1/1)
[시간 42.5] 가스켓 성형 제조 로직 완료
[시간 42.5] 가스켓 성형 출하품 운송 요청 시작
[시간 42.5] 가스켓 성형 Transport 요청을 ResourceManager에게 전달
[시간 42.5] ResourceManager: GASKET_MOLDING_PROC로부터 운송 요청 접수
[시간 42.5] ResourceManager: 운송 완료 이벤트 생성 (할당 ID: transport_GASKET_MOLDING_PROC_42.5_c4b964f3)
[시간 42.5] 가스켓 성형 Transport 요청 접수됨 - 완료까지 대기
[시간 42.5] 가스켓 성형 출력 버퍼에서 제품 제거 (운송 요청 접수 완료, 남은 개수: 0)
[시간 42.5] ResourceManager: GASKET_MOLDING_PROC 운송 요청 처리 시작 (할당 ID: transport_GASKET_MOLDING_PROC_42.5_c4b964f3)
[시간 42.5] Transport 할당 완료: transport_001 to GASKET_MOLDING_PROC (할당 ID: 3f9d7a3b-9c63-4f79-8f1e-853cc1cb9462, 대기시간: 0.0)
[시간 42.5] ResourceManager: GASKET_MOLDING_PROC 운송 할당 성공 (할당 ID: 3f9d7a3b-9c63-4f79-8f1e-853cc1cb9462)
[시간 42.5] ResourceManager: 실제 운송 처리는 TransportProcess에서 수행
[시간 42.5] ResourceManager가 TransportProcess 실행 시작: DOOR_TRANS_1 (요청자: GASKET_MOLDING_PROC)
[시간 42.5] 도어패널 운송 운송 로직 시작
[시간 42.5] 도어패널 운송 적재 중... (소요시간: 0.5)
[시간 43.0] 도어패널 운송 ✅ 적재 완료! ResourceManager에게 알림 전송
[시간 43.0] 도어패널 운송 → ResourceManager: 적재 완료 알림 (요청자: GASKET_MOLDING_PROC)
[시간 43.0] ResourceManager: GASKET_MOLDING_PROC 운송 완료 알림 전송 (성공: True)
[시간 43.0] 도어패널 운송 운송 중... (소요시간: 1.5)
[시간 43.0] 가스켓 성형 Transport 완료 알림 수신: {'allocation_id': 'transport_GASKET_MOLDING_PROC_42.5_c4b964f3', 'requester_id': 'GASKET_MOLDING_PROC', 'success': True, 'completion_time': 43.0}
[시간 43.0] 가스켓 성형 Transport 성공적으로 완료
  [시간 43.0] [OK] 가스켓 성형 완료
  [시간 43.0] [3/3] 핸들 조립 실행 중...
[시간 43.0] 핸들 조립 실행 시작
[시간 43.0] 핸들 조립 제조 로직 시작
[핸들 조립] 자원 소비 완료
[시간 44.5] 도어패널 운송 하역 중... (소요시간: 0.5)
[핸들 조립] 자원 생산 완료: 1개 (버퍼: 1/1)
[시간 44.5] 핸들 조립 제조 로직 완료
[시간 44.5] 핸들 조립 출하품 운송 요청 시작
[시간 44.5] 핸들 조립 Transport 요청을 ResourceManager에게 전달
[시간 44.5] ResourceManager: HANDLE_ASSEMBLY_PROC로부터 운송 요청 접수
[시간 44.5] ResourceManager: 운송 완료 이벤트 생성 (할당 ID: transport_HANDLE_ASSEMBLY_PROC_44.5_f42bfff8)
[시간 44.5] 핸들 조립 Transport 요청 접수됨 - 완료까지 대기
[시간 44.5] 핸들 조립 출력 버퍼에서 제품 제거 (운송 요청 접수 완료, 남은 개수: 0)
[시간 44.5] ResourceManager: HANDLE_ASSEMBLY_PROC 운송 요청 처리 시작 (할당 ID: transport_HANDLE_ASSEMBLY_PROC_44.5_f42bfff8)
[시간 44.5] Transport 할당 완료: transport_001 to HANDLE_ASSEMBLY_PROC (할당 ID: 6b030279-4289-4e6a-a0c6-8f7e0a46f74b, 대기시간: 0.0)
[시간 44.5] ResourceManager: HANDLE_ASSEMBLY_PROC 운송 할당 성공 (할당 ID: 6b030279-4289-4e6a-a0c6-8f7e0a46f74b)
[시간 44.5] ResourceManager: 실제 운송 처리는 TransportProcess에서 수행
[시간 44.5] ResourceManager가 TransportProcess 실행 시작: DOOR_TRANS_1 (요청자: HANDLE_ASSEMBLY_PROC)
[시간 44.5] 도어패널 운송 운송 로직 시작
[시간 44.5] 도어패널 운송 적재 중... (소요시간: 0.5)

=== 시간 45.0 - 냉장고 제조 시스템 상태 ===
기계 상태:
  M001: 사용중=False, 처리수=0
  M002: 사용중=False, 처리수=0
  M003: 사용중=False, 처리수=0
  M004: 사용중=False, 처리수=0
  M005: 사용중=False, 처리수=0
  M006: 사용중=False, 처리수=0
  M007: 사용중=False, 처리수=0
  M008: 사용중=False, 처리수=0
  M009: 사용중=False, 처리수=0
  M010: 사용중=False, 처리수=0
  M011: 사용중=False, 처리수=0
  M012: 사용중=False, 처리수=0
운송수단 상태:
  T001: 적재량 0/5
  T002: 적재량 0/15
  T003: 적재량 0/2
  T004: 적재량 0/3
Transport 관리 상태: 등록된 운송=5
[시간 45.0] 도어패널 운송 대기 중... (소요시간: 0.3)
[시간 45.0] 도어패널 운송 ✅ 적재 완료! ResourceManager에게 알림 전송
[시간 45.0] 도어패널 운송 → ResourceManager: 적재 완료 알림 (요청자: HANDLE_ASSEMBLY_PROC)
[시간 45.0] ResourceManager: HANDLE_ASSEMBLY_PROC 운송 완료 알림 전송 (성공: True)
[시간 45.0] 도어패널 운송 운송 중... (소요시간: 1.5)
[시간 45.0] 핸들 조립 Transport 완료 알림 수신: {'allocation_id': 'transport_HANDLE_ASSEMBLY_PROC_44.5_f42bfff8', 'requester_id': 'HANDLE_ASSEMBLY_PROC', 'success': True, 'completion_time': 45.0}
[시간 45.0] 핸들 조립 Transport 성공적으로 완료
  [시간 45.0] [OK] 핸들 조립 완료
[시간 45.0] 다중공정 그룹 실행 완료 (그룹 ID: 23f0efaf-5a28-4ed7-9f41-75550dc6258b)
  [시간 45.0] [OK] [컴프레서 테스트 & 가스켓 성형 & 핸들 조립] 완료
  [시간 45.0] [2/3] 그룹래퍼([도어패널 제조 & 도어프레임 제조]) → 도어패널 운송 → 도어프레임 운송 → 도어 어셈블리 실행 중...
[시간 45.0] 공정 체인 실행 시작 (체인 ID: f7887c98-8c4b-4c8d-b3df-e1a15cb92d9d)
총 4개의 공정을 순차 실행합니다.

[시간 45.0] [1/4] 그룹래퍼([도어패널 제조 & 도어프레임 제조]) 실행 중...
[시간 45.0] 그룹래퍼([도어패널 제조 & 도어프레임 제조]) 실행 시작
[시간 45.0] 다중공정 그룹 실행 시작 (그룹 ID: 922310b9-ca6e-42eb-89df-0069e3e36932)
순차 실행할 공정: 도어패널 제조, 도어프레임 제조
  [시간 45.0] [1/2] 도어패널 제조 실행 중...
[시간 45.0] 도어패널 제조 실행 시작
[시간 45.0] 도어패널 제조 제조 로직 시작
[도어패널 제조] 자원 소비 완료
[시간 45.3] 도어패널 운송 운송 로직 완료
[시간 45.3] ResourceManager가 TransportProcess 실행 완료: DOOR_TRANS_1
[시간 45.3] ResourceManager: 전체 운송 프로세스 완료 (적재 완료 시 이미 알림 전송됨)
[시간 46.5] 도어패널 운송 하역 중... (소요시간: 0.5)
[도어패널 제조] 자원 생산 완료: 1개 (버퍼: 1/1)
[시간 47.0] 도어패널 제조 제조 로직 완료
[시간 47.0] 도어패널 제조 출하품 운송 요청 시작
[시간 47.0] 도어패널 제조 Transport 요청을 ResourceManager에게 전달
[시간 47.0] ResourceManager: DOOR_PANEL_PROC로부터 운송 요청 접수
[시간 47.0] ResourceManager: 운송 완료 이벤트 생성 (할당 ID: transport_DOOR_PANEL_PROC_47.0_ff3b293f)
[시간 47.0] 도어패널 제조 Transport 요청 접수됨 - 완료까지 대기
[시간 47.0] 도어패널 제조 출력 버퍼에서 제품 제거 (운송 요청 접수 완료, 남은 개수: 0)
[시간 47.0] ResourceManager: DOOR_PANEL_PROC 운송 요청 처리 시작 (할당 ID: transport_DOOR_PANEL_PROC_47.0_ff3b293f)
[시간 47.0] 도어패널 운송 대기 중... (소요시간: 0.3)
[시간 47.0] Transport 할당 완료: transport_001 to DOOR_PANEL_PROC (할당 ID: 89f9a018-44a4-4c8f-95d1-00460075b1cb, 대기시간: 0.0)
[시간 47.0] ResourceManager: DOOR_PANEL_PROC 운송 할당 성공 (할당 ID: 89f9a018-44a4-4c8f-95d1-00460075b1cb)
[시간 47.0] ResourceManager: 실제 운송 처리는 TransportProcess에서 수행
[시간 47.0] ResourceManager가 TransportProcess 실행 시작: DOOR_TRANS_1 (요청자: DOOR_PANEL_PROC)
[시간 47.0] 도어패널 운송 운송 로직 시작
[시간 47.0] 도어패널 운송 적재 중... (소요시간: 0.5)
[시간 47.3] 도어패널 운송 운송 로직 완료
[시간 47.3] ResourceManager가 TransportProcess 실행 완료: DOOR_TRANS_1
[시간 47.3] ResourceManager: 전체 운송 프로세스 완료 (적재 완료 시 이미 알림 전송됨)
[시간 47.5] 도어패널 운송 ✅ 적재 완료! ResourceManager에게 알림 전송
[시간 47.5] 도어패널 운송 → ResourceManager: 적재 완료 알림 (요청자: DOOR_PANEL_PROC)
[시간 47.5] ResourceManager: DOOR_PANEL_PROC 운송 완료 알림 전송 (성공: True)
[시간 47.5] 도어패널 운송 운송 중... (소요시간: 1.5)
[시간 47.5] 도어패널 제조 Transport 완료 알림 수신: {'allocation_id': 'transport_DOOR_PANEL_PROC_47.0_ff3b293f', 'requester_id': 'DOOR_PANEL_PROC', 'success': True, 'completion_time': 47.5}
[시간 47.5] 도어패널 제조 Transport 성공적으로 완료
  [시간 47.5] [OK] 도어패널 제조 완료
  [시간 47.5] [2/2] 도어프레임 제조 실행 중...
[시간 47.5] 도어프레임 제조 실행 시작
[시간 47.5] 도어프레임 제조 제조 로직 시작
[도어프레임 제조] 자원 소비 완료
[시간 49.0] 도어패널 운송 하역 중... (소요시간: 0.5)
[시간 49.5] 도어패널 운송 대기 중... (소요시간: 0.3)
[시간 49.8] 도어패널 운송 운송 로직 완료
[시간 49.8] ResourceManager가 TransportProcess 실행 완료: DOOR_TRANS_1
[시간 49.8] ResourceManager: 전체 운송 프로세스 완료 (적재 완료 시 이미 알림 전송됨)
[도어프레임 제조] 자원 생산 완료: 1개 (버퍼: 1/1)
[시간 50.0] 도어프레임 제조 제조 로직 완료
[시간 50.0] 도어프레임 제조 출하품 운송 요청 시작
[시간 50.0] 도어프레임 제조 Transport 요청을 ResourceManager에게 전달
[시간 50.0] ResourceManager: DOOR_FRAME_PROC로부터 운송 요청 접수
[시간 50.0] ResourceManager: 운송 완료 이벤트 생성 (할당 ID: transport_DOOR_FRAME_PROC_50.0_b16ae680)
[시간 50.0] 도어프레임 제조 Transport 요청 접수됨 - 완료까지 대기
[시간 50.0] 도어프레임 제조 출력 버퍼에서 제품 제거 (운송 요청 접수 완료, 남은 개수: 0)
[시간 50.0] ResourceManager: DOOR_FRAME_PROC 운송 요청 처리 시작 (할당 ID: transport_DOOR_FRAME_PROC_50.0_b16ae680)
[시간 50.0] Transport 할당 완료: transport_001 to DOOR_FRAME_PROC (할당 ID: 52862969-d00d-4164-a98b-d5d471d50d0c, 대기시간: 0.0)
[시간 50.0] ResourceManager: DOOR_FRAME_PROC 운송 할당 성공 (할당 ID: 52862969-d00d-4164-a98b-d5d471d50d0c)
[시간 50.0] ResourceManager: 실제 운송 처리는 TransportProcess에서 수행
[시간 50.0] ResourceManager가 TransportProcess 실행 시작: DOOR_TRANS_1 (요청자: DOOR_FRAME_PROC)
[시간 50.0] 도어패널 운송 운송 로직 시작
[시간 50.0] 도어패널 운송 적재 중... (소요시간: 0.5)
[시간 50.5] 도어패널 운송 ✅ 적재 완료! ResourceManager에게 알림 전송
[시간 50.5] 도어패널 운송 → ResourceManager: 적재 완료 알림 (요청자: DOOR_FRAME_PROC)
[시간 50.5] ResourceManager: DOOR_FRAME_PROC 운송 완료 알림 전송 (성공: True)
[시간 50.5] 도어패널 운송 운송 중... (소요시간: 1.5)
[시간 50.5] 도어프레임 제조 Transport 완료 알림 수신: {'allocation_id': 'transport_DOOR_FRAME_PROC_50.0_b16ae680', 'requester_id': 'DOOR_FRAME_PROC', 'success': True, 'completion_time': 50.5}
[시간 50.5] 도어프레임 제조 Transport 성공적으로 완료
  [시간 50.5] [OK] 도어프레임 제조 완료
[시간 50.5] 다중공정 그룹 실행 완료 (그룹 ID: 922310b9-ca6e-42eb-89df-0069e3e36932)
[시간 50.5] [1/4] 그룹래퍼([도어패널 제조 & 도어프레임 제조]) 완료

[시간 50.5] [2/4] 도어패널 운송 실행 중...
[시간 50.5] 도어패널 운송 실행 시작
[경고] 기계 1에 operate 메서드가 없습니다.
[시간 50.5] 도어패널 운송 운송 로직 시작
[시간 50.5] 도어패널 운송 적재 중... (소요시간: 0.5)
[시간 51.0] 도어패널 운송 ✅ 적재 완료! ResourceManager에게 알림 전송
[시간 51.0] 도어패널 운송 ⚠️ 적재 완료 알림 생략 (필요한 정보 부족)
[시간 51.0] 도어패널 운송 운송 중... (소요시간: 1.5)
[시간 52.0] 도어패널 운송 하역 중... (소요시간: 0.5)
[시간 52.5] 도어패널 운송 하역 중... (소요시간: 0.5)
[시간 52.5] 도어패널 운송 대기 중... (소요시간: 0.3)
[시간 52.8] 도어패널 운송 운송 로직 완료
[시간 52.8] ResourceManager가 TransportProcess 실행 완료: DOOR_TRANS_1
[시간 52.8] ResourceManager: 전체 운송 프로세스 완료 (적재 완료 시 이미 알림 전송됨)
[시간 53.0] 도어패널 운송 대기 중... (소요시간: 0.3)
[시간 53.3] 도어패널 운송 운송 로직 완료
[시간 53.3] [2/4] 도어패널 운송 완료

[시간 53.3] [3/4] 도어프레임 운송 실행 중...
[시간 53.3] 도어프레임 운송 실행 시작
[경고] 기계 1에 operate 메서드가 없습니다.
[시간 53.3] 도어프레임 운송 운송 로직 시작
[시간 53.3] 도어프레임 운송 적재 중... (소요시간: 0.3)
[시간 53.6] 도어프레임 운송 ✅ 적재 완료! ResourceManager에게 알림 전송
[시간 53.6] 도어프레임 운송 ⚠️ 적재 완료 알림 생략 (필요한 정보 부족)
[시간 53.6] 도어프레임 운송 운송 중... (소요시간: 1.0)
[시간 54.6] 도어프레임 운송 하역 중... (소요시간: 0.3)
[시간 54.9] 도어프레임 운송 대기 중... (소요시간: 0.2)
[시간 55.1] 도어프레임 운송 운송 로직 완료
[시간 55.1] [3/4] 도어프레임 운송 완료

[시간 55.1] [4/4] 도어 어셈블리 실행 중...
[시간 55.1] 도어 어셈블리 실행 시작
[시간 55.1] 도어 어셈블리 조립 로직 시작
[시간 58.1] 도어 어셈블리 조립 로직 완료
[시간 58.1] 도어 어셈블리 조립품 운송 요청 시작
[시간 58.1] 도어 어셈블리 Transport 요청을 ResourceManager에게 전달
[시간 58.1] ResourceManager: DOOR_ASSEMBLY_PROC로부터 운송 요청 접수
[시간 58.1] ResourceManager: 운송 완료 이벤트 생성 (할당 ID: transport_DOOR_ASSEMBLY_PROC_58.099999999999994_58eb290b)
[시간 58.1] 도어 어셈블리 Transport 요청 접수됨 - 완료까지 대기
[시간 58.1] ResourceManager: DOOR_ASSEMBLY_PROC 운송 요청 처리 시작 (할당 ID: transport_DOOR_ASSEMBLY_PROC_58.099999999999994_58eb290b)
[시간 58.1] Transport 할당 완료: transport_001 to DOOR_ASSEMBLY_PROC (할당 ID: d243b680-04b8-4b4a-929c-c876641ed108, 대기시간: 0.0)
[시간 58.1] ResourceManager: DOOR_ASSEMBLY_PROC 운송 할당 성공 (할당 ID: d243b680-04b8-4b4a-929c-c876641ed108)
[시간 58.1] ResourceManager: 실제 운송 처리는 TransportProcess에서 수행
[시간 58.1] ResourceManager가 TransportProcess 실행 시작: DOOR_TRANS_1 (요청자: DOOR_ASSEMBLY_PROC)
[시간 58.1] 도어패널 운송 운송 로직 시작
[시간 58.1] 도어패널 운송 적재 중... (소요시간: 0.5)
[시간 58.6] 도어패널 운송 ✅ 적재 완료! ResourceManager에게 알림 전송
[시간 58.6] 도어패널 운송 → ResourceManager: 적재 완료 알림 (요청자: DOOR_ASSEMBLY_PROC)
[시간 58.6] ResourceManager: DOOR_ASSEMBLY_PROC 운송 완료 알림 전송 (성공: True)
[시간 58.6] 도어패널 운송 운송 중... (소요시간: 1.5)
[시간 58.6] 도어 어셈블리 Transport 완료 알림 수신: {'allocation_id': 'transport_DOOR_ASSEMBLY_PROC_58.099999999999994_58eb290b', 'requester_id': 'DOOR_ASSEMBLY_PROC', 'success': True, 'completion_time': 58.599999999999994}
[시간 58.6] 도어 어셈블리 Transport 성공적으로 완료
[시간 58.6] [4/4] 도어 어셈블리 완료

[시간 58.6] 공정 체인 실행 완료 (체인 ID: f7887c98-8c4b-4c8d-b3df-e1a15cb92d9d)
  [시간 58.6] [OK] 그룹래퍼([도어패널 제조 & 도어프레임 제조]) → 도어패널 운송 → 도어프레임 운송 → 도어 어셈블리 완료
  [시간 58.6] [3/3] 그룹래퍼([본체패널 제조 & 본체프레임 제조]) → 본체패널 운송 → 본체프레임 운송 → 본체 어셈블리 실행 중...
[시간 58.6] 공정 체인 실행 시작 (체인 ID: d5c8e259-10cd-405d-869f-bdd255309459)
총 4개의 공정을 순차 실행합니다.

[시간 58.6] [1/4] 그룹래퍼([본체패널 제조 & 본체프레임 제조]) 실행 중...
[시간 58.6] 그룹래퍼([본체패널 제조 & 본체프레임 제조]) 실행 시작
[시간 58.6] 다중공정 그룹 실행 시작 (그룹 ID: 3d434c58-10b8-46d9-898f-5809c58d9ab1)
순차 실행할 공정: 본체패널 제조, 본체프레임 제조
  [시간 58.6] [1/2] 본체패널 제조 실행 중...
[시간 58.6] 본체패널 제조 실행 시작
[시간 58.6] 본체패널 제조 제조 로직 시작
[본체패널 제조] 필수 자원 부족: 강판
  [시간 58.6] [ERROR] 본체패널 제조 실행 중 오류: 필요한 자원이 부족합니다
  [시간 58.6] [2/2] 본체프레임 제조 실행 중...
[시간 58.6] 본체프레임 제조 실행 시작
[시간 58.6] 본체프레임 제조 제조 로직 시작
[본체프레임 제조] 필수 자원 부족: 강판
  [시간 58.6] [ERROR] 본체프레임 제조 실행 중 오류: 필요한 자원이 부족합니다
[시간 58.6] 다중공정 그룹 실행 완료 (그룹 ID: 3d434c58-10b8-46d9-898f-5809c58d9ab1)
[시간 58.6] [1/4] 그룹래퍼([본체패널 제조 & 본체프레임 제조]) 완료

[시간 58.6] [2/4] 본체패널 운송 실행 중...
[시간 58.6] 본체패널 운송 실행 시작
[경고] 기계 1에 operate 메서드가 없습니다.
[시간 58.6] 본체패널 운송 운송 로직 시작
[시간 58.6] 본체패널 운송 적재 중... (소요시간: 0.4)
[시간 59.0] 본체패널 운송 ✅ 적재 완료! ResourceManager에게 알림 전송
[시간 59.0] 본체패널 운송 ⚠️ 적재 완료 알림 생략 (필요한 정보 부족)
[시간 59.0] 본체패널 운송 운송 중... (소요시간: 1.2)

=== 시간 60.0 - 냉장고 제조 시스템 상태 ===
기계 상태:
  M001: 사용중=False, 처리수=0
  M002: 사용중=False, 처리수=0
  M003: 사용중=False, 처리수=0
  M004: 사용중=False, 처리수=0
  M005: 사용중=False, 처리수=0
  M006: 사용중=False, 처리수=0
  M007: 사용중=False, 처리수=0
  M008: 사용중=False, 처리수=0
  M009: 사용중=False, 처리수=0
  M010: 사용중=False, 처리수=0
  M011: 사용중=False, 처리수=0
  M012: 사용중=False, 처리수=0
운송수단 상태:
  T001: 적재량 0/5
  T002: 적재량 0/15
  T003: 적재량 0/2
  T004: 적재량 0/3
Transport 관리 상태: 등록된 운송=5
[시간 60.1] 도어패널 운송 하역 중... (소요시간: 0.5)
[시간 60.2] 본체패널 운송 하역 중... (소요시간: 0.4)
[시간 60.6] 도어패널 운송 대기 중... (소요시간: 0.3)
[시간 60.6] 본체패널 운송 대기 중... (소요시간: 0.3)
[시간 60.9] 도어패널 운송 운송 로직 완료
[시간 60.9] ResourceManager가 TransportProcess 실행 완료: DOOR_TRANS_1
[시간 60.9] ResourceManager: 전체 운송 프로세스 완료 (적재 완료 시 이미 알림 전송됨)
[시간 60.9] 본체패널 운송 운송 로직 완료
[시간 60.9] [2/4] 본체패널 운송 완료

[시간 60.9] [3/4] 본체프레임 운송 실행 중...
[시간 60.9] 본체프레임 운송 실행 시작
[경고] 기계 1에 operate 메서드가 없습니다.
[시간 60.9] 본체프레임 운송 운송 로직 시작
[시간 60.9] 본체프레임 운송 적재 중... (소요시간: 0.6)
[시간 61.5] 본체프레임 운송 ✅ 적재 완료! ResourceManager에게 알림 전송
[시간 61.5] 본체프레임 운송 ⚠️ 적재 완료 알림 생략 (필요한 정보 부족)
[시간 61.5] 본체프레임 운송 운송 중... (소요시간: 2.0)
[시간 63.5] 본체프레임 운송 하역 중... (소요시간: 0.6)
[시간 64.1] 본체프레임 운송 대기 중... (소요시간: 0.4)
[시간 64.5] 본체프레임 운송 운송 로직 완료
[시간 64.5] [3/4] 본체프레임 운송 완료

[시간 64.5] [4/4] 본체 어셈블리 실행 중...
[시간 64.5] 본체 어셈블리 실행 시작
[시간 64.5] 본체 어셈블리 조립 로직 시작
[시간 68.0] 본체 어셈블리 조립 로직 완료
[시간 68.0] 본체 어셈블리 조립품 운송 요청 시작
[시간 68.0] 본체 어셈블리 Transport 요청을 ResourceManager에게 전달
[시간 68.0] ResourceManager: BODY_ASSEMBLY_PROC로부터 운송 요청 접수
[시간 68.0] ResourceManager: 운송 완료 이벤트 생성 (할당 ID: transport_BODY_ASSEMBLY_PROC_68.0_e5edd3c0)
[시간 68.0] 본체 어셈블리 Transport 요청 접수됨 - 완료까지 대기
[시간 68.0] ResourceManager: BODY_ASSEMBLY_PROC 운송 요청 처리 시작 (할당 ID: transport_BODY_ASSEMBLY_PROC_68.0_e5edd3c0)
[시간 68.0] Transport 할당 완료: transport_001 to BODY_ASSEMBLY_PROC (할당 ID: 5319c5ba-3ffc-4e30-80fd-6fc9f14b5a7d, 대기시간: 0.0)
[시간 68.0] ResourceManager: BODY_ASSEMBLY_PROC 운송 할당 성공 (할당 ID: 5319c5ba-3ffc-4e30-80fd-6fc9f14b5a7d)
[시간 68.0] ResourceManager: 실제 운송 처리는 TransportProcess에서 수행
[시간 68.0] ResourceManager가 TransportProcess 실행 시작: DOOR_TRANS_1 (요청자: BODY_ASSEMBLY_PROC)
[시간 68.0] 도어패널 운송 운송 로직 시작
[시간 68.0] 도어패널 운송 적재 중... (소요시간: 0.5)
[시간 68.5] 도어패널 운송 ✅ 적재 완료! ResourceManager에게 알림 전송
[시간 68.5] 도어패널 운송 → ResourceManager: 적재 완료 알림 (요청자: BODY_ASSEMBLY_PROC)
[시간 68.5] ResourceManager: BODY_ASSEMBLY_PROC 운송 완료 알림 전송 (성공: True)
[시간 68.5] 도어패널 운송 운송 중... (소요시간: 1.5)
[시간 68.5] 본체 어셈블리 Transport 완료 알림 수신: {'allocation_id': 'transport_BODY_ASSEMBLY_PROC_68.0_e5edd3c0', 'requester_id': 'BODY_ASSEMBLY_PROC', 'success': True, 'completion_time': 68.5}
[시간 68.5] 본체 어셈블리 Transport 성공적으로 완료
[시간 68.5] [4/4] 본체 어셈블리 완료

[시간 68.5] 공정 체인 실행 완료 (체인 ID: d5c8e259-10cd-405d-869f-bdd255309459)
  [시간 68.5] [OK] 그룹래퍼([본체패널 제조 & 본체프레임 제조]) → 본체패널 운송 → 본체프레임 운송 → 본체 어셈블리 완료
[시간 68.5] 다중공정 그룹 실행 완료 (그룹 ID: 7cf81a78-0506-46ef-a529-b14bdd88d425)
[시간 68.5] [1/5] 그룹래퍼([[컴프레서 테스트 & 가스켓 성형 & 핸들 조립] & 그룹래퍼([도어패널 제조 & 도어프레임 제조]) → 도어패널 운송 → 도어프레임 운송 → 도어 어셈블리 & 그룹래퍼([본체패널 제조 & 본체프레임 제조]) → 본체패널 운송 → 본체프레임 운송 → 본체 어셈블리]) 완료

[시간 68.5] [2/5] 최종조립 운송 실행 중...
[시간 68.5] 최종조립 운송 실행 시작
[경고] 기계 1에 operate 메서드가 없습니다.
[시간 68.5] 최종조립 운송 운송 로직 시작
[시간 68.5] 최종조립 운송 적재 중... (소요시간: 1.0)
[시간 69.5] 최종조립 운송 ✅ 적재 완료! ResourceManager에게 알림 전송
[시간 69.5] 최종조립 운송 ⚠️ 적재 완료 알림 생략 (필요한 정보 부족)
[시간 69.5] 최종조립 운송 운송 중... (소요시간: 2.5)
[시간 70.0] 도어패널 운송 하역 중... (소요시간: 0.5)
[시간 70.5] 도어패널 운송 대기 중... (소요시간: 0.3)
[시간 70.8] 도어패널 운송 운송 로직 완료
[시간 70.8] ResourceManager가 TransportProcess 실행 완료: DOOR_TRANS_1
[시간 70.8] ResourceManager: 전체 운송 프로세스 완료 (적재 완료 시 이미 알림 전송됨)
[시간 72.0] 최종조립 운송 하역 중... (소요시간: 1.0)
[시간 73.0] 최종조립 운송 대기 중... (소요시간: 0.5)
[시간 73.5] 최종조립 운송 운송 로직 완료
[시간 73.5] [2/5] 최종조립 운송 완료

[시간 73.5] [3/5] 냉장고 조립 실행 중...
[시간 73.5] 냉장고 조립 실행 시작
[시간 73.5] 냉장고 조립 조립 로직 시작

=== 시간 75.0 - 냉장고 제조 시스템 상태 ===
기계 상태:
  M001: 사용중=False, 처리수=0
  M002: 사용중=False, 처리수=0
  M003: 사용중=False, 처리수=0
  M004: 사용중=False, 처리수=0
  M005: 사용중=False, 처리수=0
  M006: 사용중=False, 처리수=0
  M007: 사용중=False, 처리수=0
  M008: 사용중=False, 처리수=0
  M009: 사용중=False, 처리수=0
  M010: 사용중=False, 처리수=0
  M011: 사용중=False, 처리수=0
  M012: 사용중=False, 처리수=0
운송수단 상태:
  T001: 적재량 0/5
  T002: 적재량 0/15
  T003: 적재량 0/2
  T004: 적재량 0/3
Transport 관리 상태: 등록된 운송=5
[시간 77.5] 냉장고 조립 조립 로직 완료
[시간 77.5] 냉장고 조립 조립품 운송 요청 시작
[시간 77.5] 냉장고 조립 Transport 요청을 ResourceManager에게 전달
[시간 77.5] ResourceManager: REFRIGERATOR_ASSEMBLY_PROC로부터 운송 요청 접수
[시간 77.5] ResourceManager: 운송 완료 이벤트 생성 (할당 ID: transport_REFRIGERATOR_ASSEMBLY_PROC_77.5_9161459a)
[시간 77.5] 냉장고 조립 Transport 요청 접수됨 - 완료까지 대기
[시간 77.5] ResourceManager: REFRIGERATOR_ASSEMBLY_PROC 운송 요청 처리 시작 (할당 ID: transport_REFRIGERATOR_ASSEMBLY_PROC_77.5_9161459a)
[시간 77.5] Transport 할당 완료: transport_001 to REFRIGERATOR_ASSEMBLY_PROC (할당 ID: 3ab4993a-3786-4f01-a4c9-7d75a62a192c, 대기시간: 0.0)
[시간 77.5] ResourceManager: REFRIGERATOR_ASSEMBLY_PROC 운송 할당 성공 (할당 ID: 3ab4993a-3786-4f01-a4c9-7d75a62a192c)
[시간 77.5] ResourceManager: 실제 운송 처리는 TransportProcess에서 수행
[시간 77.5] ResourceManager가 TransportProcess 실행 시작: DOOR_TRANS_1 (요청자: REFRIGERATOR_ASSEMBLY_PROC)
[시간 77.5] 도어패널 운송 운송 로직 시작
[시간 77.5] 도어패널 운송 적재 중... (소요시간: 0.5)
[시간 78.0] 도어패널 운송 ✅ 적재 완료! ResourceManager에게 알림 전송
[시간 78.0] 도어패널 운송 → ResourceManager: 적재 완료 알림 (요청자: REFRIGERATOR_ASSEMBLY_PROC)
[시간 78.0] ResourceManager: REFRIGERATOR_ASSEMBLY_PROC 운송 완료 알림 전송 (성공: True)
[시간 78.0] 도어패널 운송 운송 중... (소요시간: 1.5)
[시간 78.0] 냉장고 조립 Transport 완료 알림 수신: {'allocation_id': 'transport_REFRIGERATOR_ASSEMBLY_PROC_77.5_9161459a', 'requester_id': 'REFRIGERATOR_ASSEMBLY_PROC', 'success': True, 'completion_time': 78.0}
[시간 78.0] 냉장고 조립 Transport 성공적으로 완료
[시간 78.0] [3/5] 냉장고 조립 완료

[시간 78.0] [4/5] 품질검사 실행 중...
[시간 78.0] 품질검사 실행 시작
[시간 78.0] 품질검사 검사 로직 시작
[시간 79.5] 도어패널 운송 하역 중... (소요시간: 0.5)
[시간 80.0] 품질검사 검사 로직 완료
[시간 80.0] [4/5] 품질검사 완료

[시간 80.0] [5/5] 포장 실행 중...
[시간 80.0] 포장 실행 시작
[시간 80.0] 포장 제조 로직 시작
[포장] 필수 자원 부족: 원자재
[시간 80.0] [5/5] 포장 실행 중 오류: 필요한 자원이 부족합니다
냉장고 2 제조 실패: 필요한 자원이 부족합니다
[시간 80.0] 도어패널 운송 대기 중... (소요시간: 0.3)
[시간 80.3] 도어패널 운송 운송 로직 완료
[시간 80.3] ResourceManager가 TransportProcess 실행 완료: DOOR_TRANS_1
[시간 80.3] ResourceManager: 전체 운송 프로세스 완료 (적재 완료 시 이미 알림 전송됨)

=== 시간 90.0 - 냉장고 제조 시스템 상태 ===
기계 상태:
  M001: 사용중=False, 처리수=0
  M002: 사용중=False, 처리수=0
  M003: 사용중=False, 처리수=0
  M004: 사용중=False, 처리수=0
  M005: 사용중=False, 처리수=0
  M006: 사용중=False, 처리수=0
  M007: 사용중=False, 처리수=0
  M008: 사용중=False, 처리수=0
  M009: 사용중=False, 처리수=0
  M010: 사용중=False, 처리수=0
  M011: 사용중=False, 처리수=0
  M012: 사용중=False, 처리수=0
운송수단 상태:
  T001: 적재량 0/5
  T002: 적재량 0/15
  T003: 적재량 0/2
  T004: 적재량 0/3
Transport 관리 상태: 등록된 운송=5

=== 시간 105.0 - 냉장고 제조 시스템 상태 ===
기계 상태:
  M001: 사용중=False, 처리수=0
  M002: 사용중=False, 처리수=0
  M003: 사용중=False, 처리수=0
  M004: 사용중=False, 처리수=0
  M005: 사용중=False, 처리수=0
  M006: 사용중=False, 처리수=0
  M007: 사용중=False, 처리수=0
  M008: 사용중=False, 처리수=0
  M009: 사용중=False, 처리수=0
  M010: 사용중=False, 처리수=0
  M011: 사용중=False, 처리수=0
  M012: 사용중=False, 처리수=0
운송수단 상태:
  T001: 적재량 0/5
  T002: 적재량 0/15
  T003: 적재량 0/2
  T004: 적재량 0/3
Transport 관리 상태: 등록된 운송=5

=== 시간 120.0 - 냉장고 제조 시스템 상태 ===
기계 상태:
  M001: 사용중=False, 처리수=0
  M002: 사용중=False, 처리수=0
  M003: 사용중=False, 처리수=0
  M004: 사용중=False, 처리수=0
  M005: 사용중=False, 처리수=0
  M006: 사용중=False, 처리수=0
  M007: 사용중=False, 처리수=0
  M008: 사용중=False, 처리수=0
  M009: 사용중=False, 처리수=0
  M010: 사용중=False, 처리수=0
  M011: 사용중=False, 처리수=0
  M012: 사용중=False, 처리수=0
운송수단 상태:
  T001: 적재량 0/5
  T002: 적재량 0/15
  T003: 적재량 0/2
  T004: 적재량 0/3
Transport 관리 상태: 등록된 운송=5

=== 시간 135.0 - 냉장고 제조 시스템 상태 ===
기계 상태:
  M001: 사용중=False, 처리수=0
  M002: 사용중=False, 처리수=0
  M003: 사용중=False, 처리수=0
  M004: 사용중=False, 처리수=0
  M005: 사용중=False, 처리수=0
  M006: 사용중=False, 처리수=0
  M007: 사용중=False, 처리수=0
  M008: 사용중=False, 처리수=0
  M009: 사용중=False, 처리수=0
  M010: 사용중=False, 처리수=0
  M011: 사용중=False, 처리수=0
  M012: 사용중=False, 처리수=0
운송수단 상태:
  T001: 적재량 0/5
  T002: 적재량 0/15
  T003: 적재량 0/2
  T004: 적재량 0/3
Transport 관리 상태: 등록된 운송=5
=== 시뮬레이션 완료 ===

=== 냉장고 제조공정 시뮬레이션 완료 ===

```

## 로그 정보

- **파일 생성 시간**: 2025년 08월 06일 04시 56분 24초
- **시뮬레이션 유형**: 냉장고 제조공정 시뮬레이션
- **프로세스 수**: 15개 (제조, 조립, 품질검사, 운송)
- **리소스 수**: 12개 기계, 7명 작업자, 4개 운송수단, 5개 버퍼
- **저장 위치**: C:\Users\waati\Desktop\캡디\sim\manufacturing-simulation-framework\log
