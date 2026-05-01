//
//  HelpViewIOS26.swift
//  SpamKiller
//
//  Created by 김동현 on 5/1/26.
//

import SwiftUI

@available(iOS 26, *)
struct HelpViewIOS26: View {
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                VStack(alignment: .leading, spacing: 8) {
                    Text("iOS 26 사용법")
                        .font(.system(size: 24, weight: .bold))

                    Text("iOS 26에서는 메시지 필터 설정 위치와 이름이 이전 버전과 다를 수 있습니다. 아래 순서대로 확인해 주세요.")
                        .font(.system(size: 14))
                        .foregroundStyle(.secondary)
                }

                VStack(alignment: .leading, spacing: 14) {
                    HelpStepView(
                        number: "1",
                        title: "설정 앱에서 SpamKiller 또는 메시지 검색하기",
                        description: "설정 앱 상단 검색에서 SpamKiller, 메시지, 또는 message를 검색해 관련 설정으로 이동하세요."
                    )

                    HelpStepView(
                        number: "2",
                        title: "메시지 필터 관련 메뉴 열기",
                        description: "메시지 설정 안에서 스팸, 필터, 알 수 없는 발신자와 관련된 메뉴를 찾아 들어가세요."
                    )

                    HelpStepView(
                        number: "3",
                        title: "SpamKiller 활성화하기",
                        description: "필터 앱 목록이 보이면 SpamKiller를 켜거나 선택하세요."
                    )

                    HelpStepView(
                        number: "4",
                        title: "허용 번호와 스팸 키워드 등록하기",
                        description: "메인 화면에서 자주 받아야 하는 번호는 허용 번호에 추가하고, 차단할 단어는 스팸 키워드에 등록하세요."
                    )

                    HelpStepView(
                        number: "5",
                        title: "필터링 결과 확인하기",
                        description: "필터링된 문자는 메시지 앱의 정크함 또는 필터링된 메시지 영역에서 확인할 수 있습니다."
                    )

                    HelpStepView(
                        number: "6",
                        title: "로컬 AI 모드 켜기",
                        description: "설정 탭에서 로컬 AI 모드(베타 버전)를 켜면 키워드 외에도 학습된 AI가 함께 판단합니다."
                    )
                }

                VStack(alignment: .leading, spacing: 8) {
                    Text("iOS 26 참고")
                        .font(.system(size: 17, weight: .semibold))

                    Text("iOS 26은 메뉴 명칭이 달라질 수 있어 검색으로 진입하는 방법이 가장 빠를 수 있습니다. SpamKiller가 보이지 않으면 메시지 관련 설정 안의 필터 목록을 다시 확인해 주세요.")
                        .font(.system(size: 14))
                        .foregroundStyle(.secondary)
                        .fixedSize(horizontal: false, vertical: true)
                }

                Button {
                    dismiss()
                } label: {
                    Text("닫기")
                        .frame(maxWidth: .infinity)
                        .frame(height: 50)
                        .foregroundStyle(.white)
                        .background(Color(.systemGray3))
                        .cornerRadius(8)
                }
                .padding(.top, 8)
            }
            .padding(20)
        }
    }
}

@available(iOS 26, *)
#Preview {
    HelpViewIOS26()
}
