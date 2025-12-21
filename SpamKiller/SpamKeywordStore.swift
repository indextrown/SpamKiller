//
//  SpamKeywordStore.swift
//  SpamKiller
//
//  Created by 김동현 on 12/22/25.
//

import Foundation

final class SpamKeywordStore {

    private let defaults = UserDefaults(suiteName: AppGroup.id)!

    func load() -> [String] {
        defaults.stringArray(forKey: AppGroup.spamKeywordKey) ?? []
    }

    func save(_ keywords: [String]) {
        defaults.set(keywords, forKey: AppGroup.spamKeywordKey)
    }
    
    func add(_ keyword: String) {
        var list = load()
        guard !list.contains(keyword) else { return }
        list.append(keyword)
        save(list)
    }
    
    func remove(at offsets: IndexSet) {
        var list = load()
        list.remove(atOffsets: offsets)
        save(list)
    }
    
}
