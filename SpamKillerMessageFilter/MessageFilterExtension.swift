//
//  MessageFilterExtension.swift
//  SpamKillerMessageFilter
//
//  Created by 김동현 on 12/21/25.
//

import IdentityLookup

/// Message Filter Extension의 진입점 클래스.
/// 실제 메시지 필터링 로직은 프로토콜 구현(extension)에서 수행된다.
final class MessageFilterExtension: ILMessageFilterExtension {}

extension MessageFilterExtension: ILMessageFilterQueryHandling, ILMessageFilterCapabilitiesQueryHandling {
    
    /// 메시지 필터 확장이 어떤 기능을 지원하는지 iOS에 알려주는 메서드
    ///
    /// - 역할:
    ///   - 이 확장이 **어떤 유형의 메시지 분류(subAction)** 를 지원하는지 선언
    ///   - Transaction / Promotion 등의 세부 분류를 사용할 경우 여기서 설정
    ///
    /// - 호출 시점:
    ///   - 시스템이 확장의 **기능 범위(capabilities)** 를 확인할 때 호출
    ///
    /// - 주의:
    ///   - SpamKiller처럼 단순한 온디바이스 스팸 필터의 경우
    ///     구현하지 않아도 기본 동작에는 문제 없음
    ///
    /// - Parameters:
    ///   - capabilitiesQueryRequest: 시스템이 요청한 기능 정보
    ///   - context: 필터 확장 실행 컨텍스트
    ///   - completion: 지원 기능 정보를 담아 응답해야 하는 클로저
    func handle(_ capabilitiesQueryRequest: ILMessageFilterCapabilitiesQueryRequest, context: ILMessageFilterExtensionContext, completion: @escaping (ILMessageFilterCapabilitiesQueryResponse) -> Void) {
        let response = ILMessageFilterCapabilitiesQueryResponse()

        // TODO: Update subActions from ILMessageFilterSubAction enum
        // response.transactionalSubActions = [...]
        // response.promotionalSubActions   = [...]
        
        // TODO:
        // 필요한 경우 아래 subActions를 설정하여
        // promotional / transactional 메시지를 세부 분류할 수 있음
        //
        // response.transactionalSubActions = [...]
        // response.promotionalSubActions   = [...]

        completion(response)
    }
    
    /// 수신된 SMS/MMS 메시지를 분석하여 분류 결과를 반환하는 핵심 메서드
    ///
    /// - 역할:
    ///   - 메시지 텍스트 및 발신자 정보를 기반으로
    ///     허용(.allow), 정크(.junk), 광고(.promotion), 거래(.transaction) 여부를 판단
    ///
    /// - 호출 시점:
    ///   - SMS/MMS 수신 시 iOS가 자동으로 호출
    ///
    /// - 처리 흐름:
    ///   1. 오프라인 규칙 기반 판단 시도
    ///   2. 판단 가능하면 즉시 결과 반환
    ///   3. 판단 불가 시 (선택적으로) 네트워크로 판단 위임
    ///
    /// - Parameters:
    ///   - queryRequest: 수신된 메시지 정보 (일부 텍스트, 발신자 등)
    ///   - context: 필터 확장 실행 컨텍스트
    ///   - completion: 메시지 분류 결과를 담아 반환하는 클로저
    func handle(_ queryRequest: ILMessageFilterQueryRequest, context: ILMessageFilterExtensionContext, completion: @escaping (ILMessageFilterQueryResponse) -> Void) {
        
        // 1️⃣ 오프라인(온디바이스) 규칙 기반 판단
        // First, check whether to filter using offline data (if possible).
        let (offlineAction, offlineSubAction) = self.offlineAction(for: queryRequest)

        switch offlineAction {
        case .allow, .junk, .promotion, .transaction:
            /// 오프라인 판단만으로 분류가 가능한 경우
            /// → 즉시 결과 반환
            // Based on offline data, we know this message should either be Allowed, Filtered as Junk, Promotional or Transactional. Send response immediately.
            let response = ILMessageFilterQueryResponse()
            response.action = offlineAction
            response.subAction = offlineSubAction

            completion(response)

        case .none:
            /// 오프라인 규칙만으로는 판단 불가한 경우
            /// → (선택적으로) 네트워크 기반 판단으로 위임
            ///
            /// ⚠️ SpamKiller에서는 보통 사용하지 않음 (온디바이스 전용)
            // Based on offline data, we do not know whether this message should be Allowed or Filtered. Defer to network.
            // Note: Deferring requests to network requires the extension target's Info.plist to contain a key with a URL to use. See documentation for details.
            context.deferQueryRequestToNetwork() { (networkResponse, error) in
                let response = ILMessageFilterQueryResponse()
                response.action = .none
                response.subAction = .none

                if let networkResponse = networkResponse {
                    // If we received a network response, parse it to determine an action to return in our response.
                    (response.action, response.subAction) = self.networkAction(for: networkResponse)
                } else {
                    NSLog("Error deferring query request to network: \(String(describing: error))")
                }

                completion(response)
            }

        @unknown default:
            break
        }
    }

    /// 네트워크를 사용하지 않고, 온디바이스 규칙으로 메시지를 분류하는 메서드
    ///
    /// - 역할:
    ///   - 메시지 텍스트, 발신자 번호 등을 기반으로
    ///     빠르고 즉각적인 1차 스팸 판단 수행
    ///
    /// - 권장 사용:
    ///   - 키워드 기반 규칙
    ///   - 정규식
    ///   - Core ML 모델 (온디바이스)
    ///
    /// - Parameter queryRequest: 수신된 메시지 정보
    /// - Returns:
    ///   - ILMessageFilterAction: 메시지 분류 결과
    ///   - ILMessageFilterSubAction: 세부 분류 (필요 없으면 .none)
    private func offlineAction(for queryRequest: ILMessageFilterQueryRequest) -> (ILMessageFilterAction, ILMessageFilterSubAction) {
        // TODO: Replace with logic to perform offline check whether to filter first (if possible).
        // TODO:
        // SpamKiller의 핵심 로직을 여기에 구현
        
        
        let message = queryRequest.messageBody ?? ""
        
        // App Group 열기(공용 저장소)
        let defaults = UserDefaults(suiteName: AppGroup.id)
        
        // 메인 앱이 저장한 키워드 읽기
        let spamKeywords = defaults?.stringArray(forKey: AppGroup.spamKeywordKey) ?? []
        
        let isSpam = spamKeywords.contains { message.contains($0) }
        
        return isSpam ? (.junk, .none) : (.allow, .none)
        
        /*
         [기존 방식]
        // 메시지 본문
        let message = queryRequest.messageBody ?? ""
        
        // SpamKiller 1차 스팸 키워드
        let spamKeywords = [
            "대출",
            "광고",
            "무료",
            "당첨",
        ]
        
        // 키워드가 하나라도 포함되면 스팸으로 판단
        let spam: Bool = spamKeywords.contains { message.contains($0) }
        
        if spam {
            // 정크함으로 이동
            // 서브분류는 지금은 안씀
            /**
             .allow            // 정상 메시지
             .junk              // 스팸 (정크함)
             .promotion    // 광고
             .transaction  // 거래/금융
             */
            return (.junk, .none)
        } else {
            // 정상 문자
            return (.allow, .none)
        }
         */
    }

    /// 네트워크 응답을 파싱하여 메시지 분류 결과를 결정하는 메서드
    ///
    /// - 역할:
    ///   - 서버로부터 받은 판단 결과를 파싱하여
    ///     최종 메시지 분류 액션을 반환
    ///
    /// - 주의:
    ///   - 개인정보 보호 및 Extension 제약으로 인해
    ///     실제 서비스에서는 사용을 권장하지 않음
    ///
    /// - Parameter networkResponse: 네트워크 판단 결과
    /// - Returns:
    ///   - ILMessageFilterAction: 메시지 분류 결과
    ///   - ILMessageFilterSubAction: 세부 분류
    private func networkAction(for networkResponse: ILNetworkResponse) -> (ILMessageFilterAction, ILMessageFilterSubAction) {
        // TODO: Replace with logic to parse the HTTP response and data payload of `networkResponse` to return an action.
        // TODO:
        // 네트워크 응답 파싱 로직 구현
        return (.none, .none)
    }

}
