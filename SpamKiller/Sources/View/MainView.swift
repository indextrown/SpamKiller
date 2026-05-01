//
//  MainView.swift
//  SpamKiller
//
//  Created by 김동현 on 12/21/25.
//
/**
 SpamKiller는 스팸 문자를 자동 분류합니다.
 
 설정 방법:
 1. 설정 > 메시지
 2. 알 수 없는 발신자 및 스팸
 3. SpamKiller 활성화
 */

import SwiftUI

struct MainView: View {
    @EnvironmentObject var viewModel: ContentViewModel
    @AppStorage("hasShownOnboardingHelp") private var hasShownOnboardingHelp = false
    @State private var isShowingOnboardingHelp = false
    @State private var selectedComposer: ComposerType?

    private enum ComposerType: Identifiable {
        case keyword
        case allowedNumber

        var id: Int {
            switch self {
            case .keyword:
                0
            case .allowedNumber:
                1
            }
        }
    }

    var body: some View {
        NavigationStack {
            List {
                Section {
                    if viewModel.keywords.isEmpty {
                        Text("등록된 스팸 키워드가 없습니다")
                            .foregroundColor(.secondary)
                    } else {
                        ForEach(viewModel.keywords, id: \.self) { keyword in
                            Text(keyword)
                        }
                        .onDelete(perform: viewModel.deleteKeyword)
                    }
                } header: {
                    HStack {
                        Text("스팸 분류 단어 · 정크함으로 이동")
                            .font(.system(size: 14))
                        Spacer()
                        Button("추가") {
                            selectedComposer = .keyword
                        }
                        .font(.system(size: 14))
                    }
                }

                Section {
                    if viewModel.allowedNumbers.isEmpty {
                        VStack(alignment: .leading, spacing: 6) {
                            Text("등록된 허용 번호가 없습니다")
                                .foregroundColor(.secondary)
                            Text("이 번호에서 오는 문자는 스팸 필터보다 먼저 통과합니다.")
                                .font(.footnote)
                                .foregroundColor(.secondary)
                        }
                    } else {
                        ForEach(viewModel.allowedNumbers, id: \.self) { number in
                            Text(number)
                        }
                        .onDelete(perform: viewModel.deleteAllowedNumber)
                    }
                } header: {
                    HStack {
                        Text("허용 번호 · 항상 통과")
                            .font(.system(size: 14))
                        Spacer()
                        Button("추가") {
                            selectedComposer = .allowedNumber
                        }
                        .font(.system(size: 14))
                    }
                }
            }
            .navigationTitle("스팸 킬러")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button {
                        isShowingOnboardingHelp = false
                        viewModel.showHelpView = true
                    } label: {
                        Text("도움말")
                    }
                }
            }
            .onAppear {
                guard !hasShownOnboardingHelp, !viewModel.showHelpView else { return }
                isShowingOnboardingHelp = true
                viewModel.showHelpView = true
            }
            .sheet(item: $selectedComposer) { composer in
                NavigationStack {
                    addEntryView(for: composer)
                }
                .presentationDetents([.medium])
            }
            .fullScreenCover(
                isPresented: $viewModel.showHelpView,
                onDismiss: {
                    guard isShowingOnboardingHelp else { return }
                    hasShownOnboardingHelp = true
                    isShowingOnboardingHelp = false
                }
            ) {
                HelpView()
            }
        } // NavigationStack
        .overlay(alignment: .bottomTrailing) {
            Menu {
                Button("키워드 추가") {
                    selectedComposer = .keyword
                }

                Button("허용 번호 추가") {
                    selectedComposer = .allowedNumber
                }
            } label: {
                Image(systemName: "plus")
                    .font(.system(size: 22, weight: .bold))
                    .foregroundStyle(.white)
                    .frame(width: 56, height: 56)
                    .background(Color(.systemGray3))
                    .clipShape(Circle())
                    .shadow(color: .black.opacity(0.2), radius: 4, x: 0, y: 3)
            }
            .padding()
        }
    }
}

private extension MainView {
    @ViewBuilder
    private func addEntryView(for composer: ComposerType) -> some View {
        switch composer {
        case .keyword:
            Form {
                Section("새 키워드") {
                    TextField("예: 대출, 광고", text: $viewModel.newKeyword)
                }
            }
            .navigationTitle("키워드 추가")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button("취소") {
                        viewModel.newKeyword = ""
                        selectedComposer = nil
                    }
                }

                ToolbarItem(placement: .topBarTrailing) {
                    Button("저장") {
                        viewModel.addKeyword()
                        selectedComposer = nil
                    }
                }
            }

        case .allowedNumber:
            Form {
                Section("허용 번호") {
                    TextField("예: 01012345678", text: $viewModel.newAllowedNumber)
                        .keyboardType(.numberPad)
                    Text("숫자만 저장되며, 등록된 번호는 스팸 판단보다 먼저 통과합니다.")
                        .font(.footnote)
                        .foregroundColor(.secondary)
                }
            }
            .navigationTitle("허용 번호 추가")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button("취소") {
                        viewModel.newAllowedNumber = ""
                        selectedComposer = nil
                    }
                }

                ToolbarItem(placement: .topBarTrailing) {
                    Button("저장") {
                        viewModel.addAllowedNumber()
                        selectedComposer = nil
                    }
                }
            }
        }
    }
}

//#Preview {
//    MainView()
//}

#Preview {
    TabBarView()
        .preferredColorScheme(.dark)
        .environmentObject(ContentViewModel())
}

#Preview {
    SettingView()
        .preferredColorScheme(.dark)
        .environmentObject(ContentViewModel())
}
