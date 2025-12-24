//
//  SettingView.swift
//  SpamKiller
//
//  Created by 김동현 on 12/22/25.
//

import SwiftUI

struct SettingView: View {
    @EnvironmentObject var viewModel: ContentViewModel
    
    var body: some View {
        NavigationStack {
            List {
                Section {
                    Toggle(isOn: Binding(
                        get: { viewModel.isOnDeviceEnabled },
                        set: { viewModel.setOnDeviceEnabled($0) }
                    )) {
                        VStack(alignment: .leading) {
                            Text("로컬 AI 모드(베타 버전)")
                                .font(.system(size: 15))
                            Text("학습된 로컬 AI가 스팸을 차단합니다.")
                                .font(.system(size: 10))
                                .foregroundStyle(.secondary)
                                .lineLimit(1)
                        }
                    }
                } header: {
                    Text("AI 설정")
                        .font(.system(size: 14))
                }
                
                Section {
                    HStack {
                        Text("버전")
                        
                        Spacer()
                        
                        Text("1.0.0")
                    }
                } header: {
                    Text("앱 정보")
                        .font(.system(size: 14))
                }
            }
            .navigationTitle("설정")
            .navigationBarTitleDisplayMode(.inline)
        }
        
    }
}

#Preview {
    NavigationStack {
        SettingView()
            .environmentObject(ContentViewModel())
    }
}




//            Section("사용 방법") {
//                Text("이 앱은 스팸 키워드를 기준으로")
//                Text("문자를 자동으로 정크함으로 분류합니다.")
//            }
//
//            Section("초기 세팅 방법") {
//                Text("설정 > 메시지")
//                Text("> 알 수 없는 발신자 및 스팸")
//                Text("> SpamKiller 활성화")
//            }
