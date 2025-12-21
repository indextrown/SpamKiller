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

    // MARK: - Dependencies
    private let store: SpamKeywordStore

    // MARK: - Init
    init(store: SpamKeywordStore = SpamKeywordStore()) {
        self.store = store
        loadKeywords()
    }

    // MARK: - Intent (User Actions)
    func loadKeywords() {
        keywords = store.load()
    }

    func addKeyword() {
        let trimmed = newKeyword.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }

        store.add(trimmed)
        keywords = store.load()
        newKeyword = ""
    }

    func deleteKeyword(at offsets: IndexSet) {
        store.remove(at: offsets)
        keywords = store.load()
    }
}
