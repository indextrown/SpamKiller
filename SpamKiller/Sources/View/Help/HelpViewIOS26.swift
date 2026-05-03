//
//  HelpViewIOS26.swift
//  SpamKiller
//
//  Created by 김동현 on 5/1/26.
//

import SwiftUI
import UIKit

@available(iOS 26, *)
struct HelpViewIOS26: View {
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        ScrollView {
            VStack(alignment: .center, spacing: 20) {
                VStack(alignment: .center, spacing: 8) {
                    Text("Spam Killer 사용법")
                        .font(.system(size: 24, weight: .bold))
                }

                VStack(alignment: .leading, spacing: 14) {
                    HelpStepTitleOnlyView(
                        number: "1",
                        title: "아래 파란 버튼을 눌러 설정 앱을 열어 주세요."
                    )

                    Image("help26-1")
                        .resizable()
                        .aspectRatio(contentMode: .fit)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .frame(height: 50)
                        .padding(.top, 30)

                    HelpStepTitleOnlyView(
                        number: "2",
                        title: "설정 화면에서 앱을 선택해 주세요."
                    )

                    Image("help26-2")
                        .resizable()
                        .aspectRatio(contentMode: .fit)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .frame(height: 70)
                        .padding(.top, 30)

                    HelpStepTitleOnlyView(
                        number: "3",
                        title: "앱 목록에서 메시지를 찾아 선택해 주세요."
                    )

                    Image("help26-3")
                        .resizable()
                        .aspectRatio(contentMode: .fit)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .frame(height: 200)
                        .padding(.top, 30)

//                    Image("help26-4")
//                        .resizable()
//                        .aspectRatio(contentMode: .fit)
//                        .frame(maxWidth: .infinity, alignment: .leading)
//                        .frame(height: 100)

                    HelpStepTitleOnlyView(
                        number: "4",
                        title: "알 수 없는 발신자 \n-> 문자 메시지 필터링 \n-> SpamKiller를 선택해 주세요."
                    )
                }

                VStack(spacing: 12) {
                    Button {
                        openMessageSettings()
                    } label: {
                        Text("설정 열기")
                            .font(.system(size: 16, weight: .semibold))
                            .frame(maxWidth: .infinity)
                            .frame(height: 54)
                            .foregroundStyle(.white)
                            .background(
                                LinearGradient(
                                    colors: [
                                        Color.accentColor,
                                        Color.accentColor.opacity(0.82)
                                    ],
                                    startPoint: .topLeading,
                                    endPoint: .bottomTrailing
                                )
                            )
                            .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
                            .shadow(color: Color.accentColor.opacity(0.22), radius: 14, y: 8)
                    }

                    Button {
                        dismiss()
                    } label: {
                        Text("완료")
                            .font(.system(size: 16, weight: .semibold))
                            .frame(maxWidth: .infinity)
                            .frame(height: 54)
                            .foregroundStyle(Color.white.opacity(0.92))
                            .background(Color.white.opacity(0.18))
                            .overlay {
                                RoundedRectangle(cornerRadius: 16, style: .continuous)
                                    .stroke(Color.white.opacity(0.55), lineWidth: 1)
                            }
                            .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
                            .shadow(color: Color.black.opacity(0.14), radius: 10, y: 4)
                    }
                }
                .padding(.top, 20)
            }
            .padding(20)
        }
    }

    private func openMessageSettings() {
        guard let appSettingsURL = URL(string: UIApplication.openSettingsURLString) else {
            return
        }

        UIApplication.shared.open(appSettingsURL)
    }
}

@available(iOS 26, *)
#Preview {
    HelpViewIOS26()
}

//Image("help26-2")
//    .resizable()
//    .aspectRatio(contentMode: .fit)
//    .frame(maxWidth: .infinity, alignment: .leading)
//    .frame(height: 70)
//
//Image("help26-1")
//    .resizable()
//    .aspectRatio(contentMode: .fit)
//    .frame(maxWidth: .infinity, alignment: .leading)
//    .frame(height: 70)
