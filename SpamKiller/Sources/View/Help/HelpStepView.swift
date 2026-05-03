//
//  HelpStepView.swift
//  SpamKiller
//
//  Created by 김동현 on 5/1/26.
//

import SwiftUI

struct HelpStepView: View {
    let number: String
    let title: String
    let description: String

    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            Text(number)
                .font(.system(size: 14, weight: .bold))
                .foregroundStyle(.white)
                .frame(width: 28, height: 28)
                .background(Color(.systemGray3))
                .clipShape(Circle())

            VStack(alignment: .leading, spacing: 5) {
                Text(title)
                    .font(.system(size: 16, weight: .semibold))

                Text(description)
                    .font(.system(size: 14))
                    .foregroundStyle(.secondary)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
    }
}

struct HelpStepTitleOnlyView: View {
    let number: String
    let title: String

    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            Text(number)
                .font(.system(size: 14, weight: .bold))
                .foregroundStyle(.white)
                .frame(width: 28, height: 28)
                .background(Color(.systemGray3))
                .clipShape(Circle())

            Text(title)
                .font(.system(size: 16, weight: .semibold))
                .fixedSize(horizontal: false, vertical: true)
                .padding(.top, 3)
        }
    }
}
