from social_providers.twitter import Twitter

def main():

    message = """This is pretty neat. A Chinese 7.62x54mmR Type 67 general-purpose machine gun in use by Iraqi Army troops training with Italian advisors at Al Taqaddum base in 2018. The US DOD media post stands out for two very important reasons. 1) The title of the post and internal description use the local corruption for a PK-variant, a "PKC", or بكسي (alternative spelling-بيكيسي, better English spelling would be BKC) in Arabic/Kurdish. 2) The machine gun in question is a Chinese Type 67 belt-fed machine gun, possibly confused for a PK-series from a distance, the machine gun is sometimes seen in descriptions as the "بيكيسي مصريه" or Egyptian BKC.
In this case, the outstanding photo capabilities of the DOD reveal the top cover markings as follows- Factory 36, 67-2, 200504920. The receiver markings are very similar if not the same to Chinese M80 PKM-variants that flood the Middle East. 

Original Caption-  Iraqi army Gen. Khamees fires a PKC machine gun during a live-fire exercise with the Desert Battalion at Al Taqaddum, Iraq, Feb. 06, 2018. This training is part of the overall Combined Joint Task Force – Operation Inherent Resolve enhanced partner capacity mission which focuses on the training to improve the security capabilities within the nation.

Iraqi army Gen. Khamees fires a PKC machine gun during a live-fire exercise with the Desert Battalion, Source- https://www.dvidshub.net/image/4133715/pkc-live-fire
SR Reference ID-C.20201024.002, C.20200726.003"""

    twitter = Twitter()
    splittedTweet = twitter.splitMessage(message)

    for tweet in splittedTweet:
        print("/////////////////////////////////")
        print(tweet)

if __name__ == '__main__':
    main()
