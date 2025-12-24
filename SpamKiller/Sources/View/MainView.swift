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

    var body: some View {
        NavigationStack {
            List {
                if viewModel.keywords.isEmpty {
                    emptyStateView
                } else {
                    Section {
                        ForEach(viewModel.keywords, id: \.self) { keyword in
                            Text(keyword)
                        }
                        .onDelete(perform: viewModel.deleteKeyword)
                    } header: {
                        Text("스팸 분류 단어 · 정크함으로 이동")
                            .font(.system(size: 14))
                    }
                }
            }
            .navigationTitle("스팸 킬러")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button {
                        viewModel.showHelpView = true
                    } label: {
                        Text("도움말")
                        // Image(systemName: "gearshape.fill")
                    }
                }
            }
            // 키워드 추가 알림
            .alert("키워드 추가", isPresented: $viewModel.showAddAlert) {
                TextField("예: 대출, 광고", text: $viewModel.newKeyword)

                Button("추가") {
                    viewModel.addKeyword()
                }

                Button("취소", role: .cancel) {
                    viewModel.newKeyword = ""
                }
            }
            // 상태 기반 네비게이션
            .navigationDestination(isPresented: $viewModel.showHelpView) {
                HelpView()
            }
        } // NavigationStack
        .overlay(alignment: .bottomTrailing) {
            Button {
                viewModel.showAddAlert = true
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

    var emptyStateView: some View {
        VStack(spacing: 12) {
            Image(systemName: "tray")
                .font(.largeTitle)
                .foregroundColor(.secondary)

            Text("등록된 스팸 키워드가 없습니다")
                .foregroundColor(.secondary)

            Text("오른쪽 상단 + 버튼을 눌러 추가하세요")
                .font(.footnote)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 80)
        .listRowBackground(Color.clear)
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
