//
//  AllowedNumberTests.swift
//  SpamKillerTests
//
//  Created by 김동현 on 5/1/26.
//

import Testing
import SpamKillerMessageFilter

struct AllowedNumberTests {

    let ext = MessageFilterExtension()

    @Test("허용 번호와 일치하는 발신자는 .allow로 분류된다")
    func allowed_sender_returns_allow() {
        let result = ext.checkByAllowedSender(
            sender: "010-1234-5678",
            allowedNumbers: ["01012345678"]
        )
        #expect(result.0 == .allow)
        #expect(result.1 == .none)
    }

    @Test("허용 번호와 일치하지 않는 발신자는 판단을 보류한다")
    func unknown_sender_returns_none() {
        let result = ext.checkByAllowedSender(
            sender: "+82 10 9999 1111",
            allowedNumbers: ["01012345678"]
        )
        #expect(result.0 == .none)
        #expect(result.1 == .none)
    }
}
