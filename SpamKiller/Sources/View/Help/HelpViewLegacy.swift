//
//  HelpViewLegacy.swift
//  SpamKiller
//
//  Created by 김동현 on 5/1/26.
//

import SwiftUI

struct HelpViewLegacy: View {
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                VStack(alignment: .leading, spacing: 8) {
                    Text("스팸킬러 사용법")
                        .font(.system(size: 24, weight: .bold))

                    Text("처음 설치한 뒤 아래 순서대로 설정하면 스팸 문자가 자동으로 정크함으로 분류됩니다.")
                        .font(.system(size: 14))
                        .foregroundStyle(.secondary)
                }

                VStack(alignment: .leading, spacing: 14) {
                    HelpStepView(
                        number: "1",
                        title: "아이폰 설정에서 스팸킬러 켜기",
                        description: "설정 앱을 여세요."
                    )

                    Image("help1")
                        .resizable()
                        .aspectRatio(contentMode: .fit)
                        .frame(width: 70, height: 70)

                    HelpStepView(
                        number: "2",
                        title: "메시지 설정 찾기",
                        description: "설정에서 message를 검색한 뒤 메시지 메뉴로 이동하세요."
                    )

                    Image("help2")
                        .resizable()
                        .aspectRatio(contentMode: .fit)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .frame(height: 70)

                    HelpStepView(
                        number: "3",
                        title: "알 수 없는 발신자 및 스팸 선택하기",
                        description: "메시지 설정에서 알 수 없는 연락처 및 스팸을 선택한 뒤 SpamKiller를 활성화하세요."
                    )

                    Image("help3")
                        .resizable()
                        .aspectRatio(contentMode: .fit)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .frame(height: 70)

                    HelpStepView(
                        number: "4",
                        title: "스팸 키워드 등록하기",
                        description: "메인 화면 오른쪽 아래 + 버튼을 눌러 차단하고 싶은 단어를 추가하세요. 예: 광고, 대출, 이벤트"
                    )

                    HelpStepView(
                        number: "5",
                        title: "스팸 문자는 정크함에서 확인하기",
                        description: "등록한 키워드가 포함된 문자는 메시지 앱의 정크함으로 자동 분류됩니다."
                    )

                    HelpStepView(
                        number: "6",
                        title: "로컬 AI 모드 사용하기",
                        description: "설정 탭에서 로컬 AI 모드(베타 버전)를 켜면 학습된 AI가 스팸 여부를 함께 판단합니다."
                    )
                }

                VStack(alignment: .leading, spacing: 8) {
                    Text("알아두기")
                        .font(.system(size: 17, weight: .semibold))

                    Text("SpamKiller는 사용자가 등록한 키워드와 로컬 AI 설정을 기준으로 문자 내용을 기기 안에서 분류합니다. 필터링 기능을 사용하려면 iOS 설정에서 SpamKiller가 켜져 있어야 합니다.")
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
    HelpViewLegacy()
}
