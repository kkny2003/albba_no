
================================================================================
분리된 구조의 ManufacturingProcess + ResourceManager + TransportProcess
================================================================================
구조:
1. ManufacturingProcess: 운송 요청만 보냄
2. ResourceManager: 운송 요청 관리 및 TransportProcess 할당
3. TransportProcess: 실제 운송 처리
================================================================================
[시간 0.0] 고급 자원 등록 (우선순위 지원): transport (용량: 2, 타입: ResourceType.TRANSPORT)
[자동_운송공정] 공정 초기화 완료 - 기계: transport_vehicle_001 / 작업자: transport_worker_001
[자동_운송공정] 한번 실행당 생산량: 1개
[자동_운송공정] 운송 경로 설정: 제조공장 → 중간창고 → 최종목적지
[시간 0.0] TransportProcess 등록: transport_main (프로세스 ID: transport_001)
[시간 0.0] TransportProcess ResourceManager에 등록 완료
[분리구조_제조공정1] 공정 초기화 완료 - 기계: machine_001 / 작업자: worker_001
[분리구조_제조공정1] 한번 실행당 생산량: 1개
[분리구조_제조공정1] Transport 설정 - 자동 운송: 활성화
[시간 0.0] ManufacturingProcess 생성 완료 - 운송 요청만 담당

[시간 0.0] 분리구조 시뮬레이션 시작


======================================================================
분리구조 제조 사이클 1/4 시작
======================================================================

[시간 0.0] === 분리구조 제조 사이클 시작 ===
[시간 0.0] 분리구조_제조공정1 제조 로직 시작
[분리구조_제조공정1] 자원 소비 완료
[분리구조_제조공정1] 자원 생산 완료: 1개 (버퍼: 1/1)
[시간 2.0] 분리구조_제조공정1 제조 로직 완료
[시간 2.0] 분리구조_제조공정1 출하품 운송 요청 시작
[시간 2.0] 분리구조_제조공정1 Transport 요청을 ResourceManager에게 전달
[시간 2.0] ResourceManager: mfg_separated_001로부터 운송 요청 접수
[시간 2.0] ResourceManager: 운송 완료 이벤트 생성 (할당 ID: transport_mfg_separated_001_2.0_d8529034)
[시간 2.0] 분리구조_제조공정1 Transport 요청 접수됨 - 완료까지 대기
[시간 2.0] 분리구조_제조공정1 출력 버퍼에서 제품 제거 (운송 요청 접수 완료, 남은 개수: 0)
[시간 2.0] ResourceManager: mfg_separated_001 운송 요청 처리 시작 (할당 ID: transport_mfg_separated_001_2.0_d8529034)
[시간 2.0] Transport 할당 완료: transport_main to mfg_separated_001 (할당 ID: df0e46f0-c145-4f81-bd2e-fac64d8f2b10, 대기시간: 0.0)   
[시간 2.0] ResourceManager: mfg_separated_001 운송 할당 성공 (할당 ID: df0e46f0-c145-4f81-bd2e-fac64d8f2b10)
[시간 2.0] ResourceManager: 실제 운송 처리는 TransportProcess에서 수행
[시간 2.0] ResourceManager가 TransportProcess 실행 시작: transport_001 (요청자: mfg_separated_001)
[시간 2.0] 자동_운송공정 운송 로직 시작
[시간 2.0] 자동_운송공정 적재 중... (소요시간: 0.3)
[시간 2.3] 자동_운송공정 ✅ 적재 완료! ResourceManager에게 알림 전송
[시간 2.3] 자동_운송공정 → ResourceManager: 적재 완료 알림 (요청자: mfg_separated_001)
[시간 2.3] ResourceManager: mfg_separated_001 운송 완료 알림 전송 (성공: True)
[시간 2.3] 자동_운송공정 운송 중... (소요시간: 1.5)
[시간 2.3] 분리구조_제조공정1 Transport 완료 알림 수신: {'allocation_id': 'transport_mfg_separated_001_2.0_d8529034', 'requester_id': 'mfg_separated_001', 'success': True, 'completion_time': 2.3}
[시간 2.3] 분리구조_제조공정1 Transport 성공적으로 완료
[시간 2.3] === 분리구조 제조 사이클 완료 ===
[시간 2.3] (운송은 ResourceManager와 TransportProcess가 별도로 처리)

[시간 3.8] 자동_운송공정 하역 중... (소요시간: 0.2)
[시간 4.0] 자동_운송공정 대기 중... (소요시간: 0.2)
[시간 4.2] 자동_운송공정 운송 로직 완료
[시간 4.2] ResourceManager가 TransportProcess 실행 완료: transport_001
[시간 4.2] ResourceManager: 전체 운송 프로세스 완료 (적재 완료 시 이미 알림 전송됨)

======================================================================
분리구조 제조 사이클 2/4 시작
======================================================================

[시간 4.3] === 분리구조 제조 사이클 시작 ===
[시간 4.3] 분리구조_제조공정1 제조 로직 시작
[분리구조_제조공정1] 자원 소비 완료
[분리구조_제조공정1] 자원 생산 완료: 1개 (버퍼: 1/1)
[시간 6.3] 분리구조_제조공정1 제조 로직 완료
[시간 6.3] 분리구조_제조공정1 출하품 운송 요청 시작
[시간 6.3] 분리구조_제조공정1 Transport 요청을 ResourceManager에게 전달
[시간 6.3] ResourceManager: mfg_separated_001로부터 운송 요청 접수
[시간 6.3] ResourceManager: 운송 완료 이벤트 생성 (할당 ID: transport_mfg_separated_001_6.3_64462123)
[시간 6.3] 분리구조_제조공정1 Transport 요청 접수됨 - 완료까지 대기
[시간 6.3] 분리구조_제조공정1 출력 버퍼에서 제품 제거 (운송 요청 접수 완료, 남은 개수: 0)
[시간 6.3] ResourceManager: mfg_separated_001 운송 요청 처리 시작 (할당 ID: transport_mfg_separated_001_6.3_64462123)
[시간 6.3] Transport 할당 완료: transport_main to mfg_separated_001 (할당 ID: 1fc02438-6fbf-47b9-a30d-28af85d1f652, 대기시간: 0.0)   
[시간 6.3] ResourceManager: mfg_separated_001 운송 할당 성공 (할당 ID: 1fc02438-6fbf-47b9-a30d-28af85d1f652)
[시간 6.3] ResourceManager: 실제 운송 처리는 TransportProcess에서 수행
[시간 6.3] ResourceManager가 TransportProcess 실행 시작: transport_001 (요청자: mfg_separated_001)
[시간 6.3] 자동_운송공정 운송 로직 시작
[시간 6.3] 자동_운송공정 적재 중... (소요시간: 0.3)
[시간 6.6] 자동_운송공정 ✅ 적재 완료! ResourceManager에게 알림 전송
[시간 6.6] 자동_운송공정 → ResourceManager: 적재 완료 알림 (요청자: mfg_separated_001)
[시간 6.6] ResourceManager: mfg_separated_001 운송 완료 알림 전송 (성공: True)
[시간 6.6] 자동_운송공정 운송 중... (소요시간: 1.5)
[시간 6.6] 분리구조_제조공정1 Transport 완료 알림 수신: {'allocation_id': 'transport_mfg_separated_001_6.3_64462123', 'requester_id': 'mfg_separated_001', 'success': True, 'completion_time': 6.6}
[시간 6.6] 분리구조_제조공정1 Transport 성공적으로 완료
[시간 6.6] === 분리구조 제조 사이클 완료 ===
[시간 6.6] (운송은 ResourceManager와 TransportProcess가 별도로 처리)

[시간 8.1] 자동_운송공정 하역 중... (소요시간: 0.2)
[시간 8.3] 자동_운송공정 대기 중... (소요시간: 0.2)
[시간 8.5] 자동_운송공정 운송 로직 완료
[시간 8.5] ResourceManager가 TransportProcess 실행 완료: transport_001
[시간 8.5] ResourceManager: 전체 운송 프로세스 완료 (적재 완료 시 이미 알림 전송됨)

======================================================================
분리구조 제조 사이클 3/4 시작
======================================================================

[시간 8.6] === 분리구조 제조 사이클 시작 ===
[시간 8.6] 분리구조_제조공정1 제조 로직 시작
[분리구조_제조공정1] 자원 소비 완료
[분리구조_제조공정1] 자원 생산 완료: 1개 (버퍼: 1/1)
[시간 10.6] 분리구조_제조공정1 제조 로직 완료
[시간 10.6] 분리구조_제조공정1 출하품 운송 요청 시작
[시간 10.6] 분리구조_제조공정1 Transport 요청을 ResourceManager에게 전달
[시간 10.6] ResourceManager: mfg_separated_001로부터 운송 요청 접수
[시간 10.6] ResourceManager: 운송 완료 이벤트 생성 (할당 ID: transport_mfg_separated_001_10.6_1fbdc414)
[시간 10.6] 분리구조_제조공정1 Transport 요청 접수됨 - 완료까지 대기
[시간 10.6] 분리구조_제조공정1 출력 버퍼에서 제품 제거 (운송 요청 접수 완료, 남은 개수: 0)
[시간 10.6] ResourceManager: mfg_separated_001 운송 요청 처리 시작 (할당 ID: transport_mfg_separated_001_10.6_1fbdc414)
[시간 10.6] Transport 할당 완료: transport_main to mfg_separated_001 (할당 ID: a422ca8e-76d6-432d-a576-638aec6796d8, 대기시간: 0.0)  
[시간 10.6] ResourceManager: mfg_separated_001 운송 할당 성공 (할당 ID: a422ca8e-76d6-432d-a576-638aec6796d8)
[시간 10.6] ResourceManager: 실제 운송 처리는 TransportProcess에서 수행
[시간 10.6] ResourceManager가 TransportProcess 실행 시작: transport_001 (요청자: mfg_separated_001)
[시간 10.6] 자동_운송공정 운송 로직 시작
[시간 10.6] 자동_운송공정 적재 중... (소요시간: 0.3)
[시간 10.9] 자동_운송공정 ✅ 적재 완료! ResourceManager에게 알림 전송
[시간 10.9] 자동_운송공정 → ResourceManager: 적재 완료 알림 (요청자: mfg_separated_001)
[시간 10.9] ResourceManager: mfg_separated_001 운송 완료 알림 전송 (성공: True)
[시간 10.9] 자동_운송공정 운송 중... (소요시간: 1.5)
[시간 10.9] 분리구조_제조공정1 Transport 완료 알림 수신: {'allocation_id': 'transport_mfg_separated_001_10.6_1fbdc414', 'requester_id': 'mfg_separated_001', 'success': True, 'completion_time': 10.9}
[시간 10.9] 분리구조_제조공정1 Transport 성공적으로 완료
[시간 10.9] === 분리구조 제조 사이클 완료 ===
[시간 10.9] (운송은 ResourceManager와 TransportProcess가 별도로 처리)


[시간 12.0] === 분리구조 시스템 상태 모니터링 ===
제조공정 입력자원 수: 4
제조공정 출력자원 수: 1
등록된 TransportProcess: 1개
Transport 자원 상태: 0/2 사용중
  - transport_main: 자동_운송공정 (상태: 대기)
============================================================

[시간 12.4] 자동_운송공정 하역 중... (소요시간: 0.2)
[시간 12.6] 자동_운송공정 대기 중... (소요시간: 0.2)
[시간 12.8] 자동_운송공정 운송 로직 완료
[시간 12.8] ResourceManager가 TransportProcess 실행 완료: transport_001
[시간 12.8] ResourceManager: 전체 운송 프로세스 완료 (적재 완료 시 이미 알림 전송됨)

======================================================================
분리구조 제조 사이클 4/4 시작
======================================================================

[시간 12.9] === 분리구조 제조 사이클 시작 ===
[시간 12.9] 분리구조_제조공정1 제조 로직 시작
[분리구조_제조공정1] 자원 소비 완료
[분리구조_제조공정1] 자원 생산 완료: 1개 (버퍼: 1/1)
[시간 14.9] 분리구조_제조공정1 제조 로직 완료
[시간 14.9] 분리구조_제조공정1 출하품 운송 요청 시작
[시간 14.9] 분리구조_제조공정1 Transport 요청을 ResourceManager에게 전달
[시간 14.9] ResourceManager: mfg_separated_001로부터 운송 요청 접수
[시간 14.9] ResourceManager: 운송 완료 이벤트 생성 (할당 ID: transport_mfg_separated_001_14.9_449a2e8c)
[시간 14.9] 분리구조_제조공정1 Transport 요청 접수됨 - 완료까지 대기
[시간 14.9] 분리구조_제조공정1 출력 버퍼에서 제품 제거 (운송 요청 접수 완료, 남은 개수: 0)
[시간 14.9] ResourceManager: mfg_separated_001 운송 요청 처리 시작 (할당 ID: transport_mfg_separated_001_14.9_449a2e8c)
[시간 14.9] Transport 할당 완료: transport_main to mfg_separated_001 (할당 ID: 0ab9ce2e-c103-4e15-9dc1-4b9705fb46ae, 대기시간: 0.0)  
[시간 14.9] ResourceManager: mfg_separated_001 운송 할당 성공 (할당 ID: 0ab9ce2e-c103-4e15-9dc1-4b9705fb46ae)
[시간 14.9] ResourceManager: 실제 운송 처리는 TransportProcess에서 수행
[시간 14.9] ResourceManager가 TransportProcess 실행 시작: transport_001 (요청자: mfg_separated_001)
[시간 14.9] 자동_운송공정 운송 로직 시작
[시간 14.9] 자동_운송공정 적재 중... (소요시간: 0.3)
[시간 15.2] 자동_운송공정 ✅ 적재 완료! ResourceManager에게 알림 전송
[시간 15.2] 자동_운송공정 → ResourceManager: 적재 완료 알림 (요청자: mfg_separated_001)
[시간 15.2] ResourceManager: mfg_separated_001 운송 완료 알림 전송 (성공: True)
[시간 15.2] 자동_운송공정 운송 중... (소요시간: 1.5)
[시간 15.2] 분리구조_제조공정1 Transport 완료 알림 수신: {'allocation_id': 'transport_mfg_separated_001_14.9_449a2e8c', 'requester_id': 'mfg_separated_001', 'success': True, 'completion_time': 15.200000000000001}
[시간 15.2] 분리구조_제조공정1 Transport 성공적으로 완료
[시간 15.2] === 분리구조 제조 사이클 완료 ===
[시간 15.2] (운송은 ResourceManager와 TransportProcess가 별도로 처리)

[시간 16.7] 자동_운송공정 하역 중... (소요시간: 0.2)
[시간 16.9] 자동_운송공정 대기 중... (소요시간: 0.2)
[시간 17.1] 자동_운송공정 운송 로직 완료
[시간 17.1] ResourceManager가 TransportProcess 실행 완료: transport_001
[시간 17.1] ResourceManager: 전체 운송 프로세스 완료 (적재 완료 시 이미 알림 전송됨)

[시간 24.0] === 분리구조 시스템 상태 모니터링 ===
제조공정 입력자원 수: 4
제조공정 출력자원 수: 1
등록된 TransportProcess: 1개
Transport 자원 상태: 0/2 사용중
  - transport_main: 자동_운송공정 (상태: 대기)
============================================================


[시간 36.0] === 분리구조 시스템 상태 모니터링 ===
제조공정 입력자원 수: 4
제조공정 출력자원 수: 1
등록된 TransportProcess: 1개
Transport 자원 상태: 0/2 사용중
  - transport_main: 자동_운송공정 (상태: 대기)
============================================================


[시간 48.0] === 분리구조 시스템 상태 모니터링 ===
제조공정 입력자원 수: 4
제조공정 출력자원 수: 1
등록된 TransportProcess: 1개
Transport 자원 상태: 0/2 사용중
  - transport_main: 자동_운송공정 (상태: 대기)
============================================================


================================================================================
분리구조 시뮬레이션 완료 - 최종 결과
================================================================================
제조공정 입력자원 수: 4
제조공정 출력자원 수: 1
ResourceManager 등록된 TransportProcess: 1개
총 자원 요청: 0
성공한 할당: 4
성공률: 0.0%

분리된 구조의 장점:
1. 책임 분리: 각 컴포넌트가 명확한 역할을 담당
2. 확장성: ResourceManager에서 여러 TransportProcess 관리 가능
3. 재사용성: 하나의 TransportProcess를 여러 제조공정에서 공유
4. 유지보수성: 운송 로직 변경 시 TransportProcess만 수정
5. 테스트 용이성: 각 컴포넌트를 독립적으로 테스트 가능
