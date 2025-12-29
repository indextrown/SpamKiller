//
//  HelpView.swift
//  SpamKiller
//
//  Created by 김동현 on 12/24/25.
//

import SwiftUI

struct HelpView: View {
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 5) {
                
                // MARK: - Title
                Text("스팸킬러 사용법")
                    .font(.system(size: 20, weight: .bold))
                
                // MARK: - 1
                Image("help1")
                    .resizable()
                    .aspectRatio(contentMode: .fit)
                    .frame(width: 70, height: 70)
                
                Text("- 설정을 클릭합니다.")
                    .font(.system(size: 12, weight: .light))
                    .padding(.bottom, 20)
                   
                // MARK: - 2
                Image("help2")
                    .resizable()
                    .frame(width: 300, height: 70)
                
                Text("- message를 검색합니다.")
                    .font(.system(size: 12, weight: .light))
                    .padding(.bottom, 20)
                
                // MARK: - 3
                Image("help3")
                    .resizable()
                    .frame(width: 300, height: 70)
                
                Text("- 알 수 없는 연락처 및 스팸을 클릭합니다.")
                    .font(.system(size: 12, weight: .light))
                    .padding(.bottom, 20)
                
                /*
                Button("설정으로 이동") {
                    if let url = URL(string: UIApplication.openSettingsURLString) {
                        UIApplication.shared.open(url)
                    }
                }
                 */
                
                Button {
                    dismiss()
                } label: {
                    Text("닫기")
                        .frame(maxWidth: .infinity)
                        .frame(height: 50)
                        .foregroundStyle(.white)
                        .background(Color(.systemGray3))
                        .cornerRadius(10)
                }
            }
            // .frame(minHeight: UIScreen.main.bounds.height)
            .padding(.horizontal, 20)
        }
    }
}

#Preview {
    HelpView()
}
