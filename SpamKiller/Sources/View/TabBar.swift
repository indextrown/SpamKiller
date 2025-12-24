//
//  TabBar.swift
//  SpamKiller
//
//  Created by 김동현 on 12/24/25.
//

import SwiftUI

struct TabBarView: View {
    @State private var selectedTab: Int = 1
    @StateObject private var viewModel = ContentViewModel()
    
    var body: some View {
        TabView(selection: $selectedTab) {
            MainView()
                .tabItem {
                    Image(systemName: "list.bullet")
                    Text("키워드")
                }
                .tag(1)
            
                
            SettingView()
                .tabItem {
                    Image(systemName: "gear")
                    Text("설정")
                }
                .tag(2)
        }
        .font(.headline)
        .environmentObject(viewModel)
    }
}

#Preview {
    TabBarView()
}
