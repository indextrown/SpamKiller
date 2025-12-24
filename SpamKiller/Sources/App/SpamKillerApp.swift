//
//  SpamKillerApp.swift
//  SpamKiller
//
//  Created by 김동현 on 12/21/25.
//

import SwiftUI
import UIKit

@main
struct SpamKillerApp: App {
    
    init() {
        let appearance = UINavigationBarAppearance()
        appearance.configureWithDefaultBackground() // 기본 머티리얼(블러 느낌)

        UINavigationBar.appearance().standardAppearance = appearance
        UINavigationBar.appearance().scrollEdgeAppearance = appearance
        UINavigationBar.appearance().compactAppearance = appearance
    }
    
    var body: some Scene {
        WindowGroup {
            TabBarView()
//                .preferredColorScheme(.dark)
            
//            MainView()
//                .preferredColorScheme(.dark)
        }
    }
}
