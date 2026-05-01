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
    @Published var allowedNumbers: [String] = []
    @Published var newKeyword: String = ""
    @Published var newAllowedNumber: String = ""
    @Published var showAddAlert: Bool = false
    @Published var showAddAllowedNumberAlert: Bool = false
    @Published var showHelpView: Bool = false
    @Published var isOnDeviceEnabled: Bool = false

    // MARK: - Init
    init() {
        loadKeywords()
        loadAllowedNumbers()
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

// MARK: - Allowed Numbers
extension ContentViewModel {
    func loadAllowedNumbers() {
        allowedNumbers = SharedStore.shared.loadAllowedNumbers()
    }

    func addAllowedNumber() {
        SharedStore.shared.addAllowedNumber(newAllowedNumber)
        allowedNumbers = SharedStore.shared.loadAllowedNumbers()
        newAllowedNumber = ""
    }

    func deleteAllowedNumber(at offsets: IndexSet) {
        SharedStore.shared.removeAllowedNumbers(at: offsets)
        allowedNumbers = SharedStore.shared.loadAllowedNumbers()
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
