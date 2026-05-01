//
//  SettingView.swift
//  SpamKiller
//
//  Created by 김동현 on 12/22/25.
//

import SwiftUI

struct SettingView: View {
    @EnvironmentObject var viewModel: ContentViewModel
    @Environment(\.openURL) private var openURL
    @State private var showFilteredMessagesGuide = false
    
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
                    HStack(spacing: 10) {
                        Circle()
                            .fill(protectionStatusColor)
                            .frame(width: 10, height: 10)
                        
                        VStack(alignment: .leading, spacing: 4) {
                            Text("보호 상태")
                            
                            Text(protectionStatusText)
                                .font(.system(size: 11))
                                .foregroundStyle(.secondary)
                        }
                    }
                    
                    Button {
                        showFilteredMessagesGuide = true
                    } label: {
                        HStack {
                            VStack(alignment: .leading, spacing: 4) {
                                Text("필터링된 메시지 확인")
                                
                                Text("메시지 앱의 정크함에서 확인할 수 있습니다.")
                                    .font(.system(size: 11))
                                    .foregroundStyle(.secondary)
                            }
                            
                            Spacer()
                            
                            Image(systemName: "message")
                                .foregroundStyle(.secondary)
                        }
                    }
                    .foregroundStyle(.primary)
                } header: {
                    Text("메시지")
                        .font(.system(size: 14))
                }
                
                Section {
                    HStack {
                        Text("버전")
                        
                        Spacer()
                        
                        Text("1.0.0")
                    }
                    
                    Button {
                        openMail()
                    } label: {
                        HStack {
                            Text("문의하기")
                            
                            Spacer()
                            
                            Image(systemName: "envelope")
                                .foregroundStyle(.secondary)
                        }
                    }
                    .foregroundStyle(.primary)
                } header: {
                    Text("앱 정보")
                        .font(.system(size: 14))
                }
            }
            .navigationTitle("설정")
            .navigationBarTitleDisplayMode(.inline)
            .alert("필터링된 메시지 확인", isPresented: $showFilteredMessagesGuide) {
                Button("확인", role: .cancel) {}
            } message: {
                Text("홈 화면 > 메시지 앱 > 왼쪽 상단 필터 또는 목록 > 정크함")
            }
        }
        
    }
    
    private func openMail() {
        let subject = "SpamKiller 문의"
        let encodedSubject = subject.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? subject
        guard let url = URL(string: "mailto:indextrown@gmail.com?subject=\(encodedSubject)") else { return }
        openURL(url)
    }
    
    private var protectionStatusText: String {
        switch (viewModel.keywords.isEmpty, viewModel.isOnDeviceEnabled) {
        case (false, true):
            return "단어 + 로컬 AI 기반 필터링"
        case (false, false):
            return "단어 기반 필터링"
        case (true, true):
            return "로컬 AI 기반 필터링"
        case (true, false):
            return "필터링 설정이 필요합니다"
        }
    }
    
    private var protectionStatusColor: Color {
        viewModel.keywords.isEmpty && !viewModel.isOnDeviceEnabled ? .orange : .green
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
