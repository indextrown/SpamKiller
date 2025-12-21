//
//  SettingView.swift
//  SpamKiller
//
//  Created by 김동현 on 12/22/25.
//

import SwiftUI

struct SettingView: View {

    var body: some View {
        List {
            Section("사용 방법") {
                Text("이 앱은 스팸 키워드를 기준으로")
                Text("문자를 자동으로 정크함으로 분류합니다.")
            }

            Section("초기 세팅 방법") {
                Text("설정 > 메시지")
                Text("> 알 수 없는 발신자 및 스팸")
                Text("> SpamKiller 활성화")
            }

            Section("앱 정보") {
                Text("버전 1.0.0")
            }
        }
        .navigationTitle("설정")
        .navigationBarTitleDisplayMode(.inline)
    }
}

#Preview {
    NavigationStack {
        SettingView()
    }
}

//import SwiftUI
//
//struct SettingView: View {
//
//    var body: some View {
//        List {
//            VStack(alignment: .leading, spacing: 8) {
//                Text("사용 방법")
//                    .font(.headline)
//
//                Text("이 앱은 스팸 키워드를 기준으로")
//                Text("문자를 자동으로 정크함으로 분류합니다.")
//            }
//            .padding(.vertical, 8)
//
//            VStack(alignment: .leading, spacing: 8) {
//                Text("설정 경로")
//                    .font(.headline)
//
//                Text("설정 > 메시지")
//                Text("알 수 없는 발신자 및 스팸")
//                Text("SpamKiller 활성화")
//            }
//            .padding(.vertical, 8)
//
//            VStack(alignment: .leading, spacing: 8) {
//                Text("앱 정보")
//                    .font(.headline)
//
//                Text("버전 1.0.0")
//                    .foregroundColor(.secondary)
//            }
//            .padding(.vertical, 8)
//        }
//        .listStyle(.plain)
//        .navigationTitle("설정")
//        .navigationBarTitleDisplayMode(.inline)
//    }
//}
//
//#Preview {
//    NavigationStack {
//        SettingView()
//    }
//}
