//
//  ContentViewModel.swift
//  SpamKiller
//
//  Created by 김동현 on 12/22/25.
//

import SwiftUI

final class ContentViewModel: ObservableObject {

    // MARK: - Published State
    @Published var keywords: [String] = []
    @Published var newKeyword: String = ""
    @Published var showAddAlert: Bool = false
    @Published var showHelpView: Bool = false
    @Published var isOnDeviceEnabled: Bool = false

    // MARK: - Init
    init() {
        loadKeywords()
        loadOnDeviceToggle()
    }
}

// MARK: - Keyword
extension ContentViewModel {
    
    func loadKeywords() {
        keywords = SharedStore.shared.loadSpamKeywords()
    }

    func addKeyword() {
        SharedStore.shared.addSpamKeyword(keyword: newKeyword)
        keywords = SharedStore.shared.loadSpamKeywords()
        newKeyword = ""
    }
    
    func deleteKeyword(at offsets: IndexSet) {
        SharedStore.shared.removeSpamKeywords(at: offsets)
        keywords = SharedStore.shared.loadSpamKeywords()
    }
}

// MARK: - On-Device AI
extension ContentViewModel {
    
    func loadOnDeviceToggle() {
        isOnDeviceEnabled = SharedStore.shared.isOnDeviceEnabled()
    }

    func setOnDeviceEnabled(_ enabled: Bool) {
        isOnDeviceEnabled = enabled
        SharedStore.shared.setOnDeviceEnabled(enabled)
    }
}
