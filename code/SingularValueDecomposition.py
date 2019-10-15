from sklearn.decomposition import TruncatedSVD
from scipy.linalg import svd
import numpy as np
import pymongo
import os
import shutil

client = pymongo.MongoClient('localhost', 27018)
imagedb = client["imagedb"]
mydb = imagedb["image_models"]


class SVD(object):

    def createKLatentSymantics(self, model, k):
        #svd1 = TruncatedSVD(k)
        model = "bag_" + model
        feature_desc = []
        img_list = []
        for descriptor in imagedb.image_models.find():
            feature_desc.append(descriptor[model])
            img_list.append(descriptor["_id"])

        #feature_desc_transformed = svd1.fit_transform(feature_desc)
        U, S, V = svd(feature_desc, full_matrices=False)

        for i in range(k):
            col = U[:, i]
            arr = []
            for k, val in enumerate(col):
                arr.append((str(img_list[k]), val))
            arr.sort(key=lambda x: x[1], reverse=True)
            print("Printing term-weight pair for latent Symantic {}({}):".format(i + 1, S[i]))
            print(arr)

    def mSimilarImage(self, imgLoc, model, k, m):
        img_list = []
        svd = TruncatedSVD(k)
        model = "bag_" + model
        feature_desc = []
        img_list = []
        for descriptor in imagedb.image_models.find():
            feature_desc.append(descriptor[model])
            img_list.append(descriptor["_id"])

        feature_desc_transformed = svd.fit_transform(feature_desc)

        head, tail = os.path.split(imgLoc)

        id = img_list.index(tail)

        rank_dict = {}
        for i, row in enumerate(feature_desc_transformed):
            if (i == id):
                continue
            euc_dis = np.square(np.subtract(feature_desc_transformed[id], feature_desc_transformed[i]))
            match_score = np.sqrt(euc_dis.sum(0))
            rank_dict[img_list[i]] = match_score

        res_dir = os.path.join('..', 'output', model[4:], 'match')
        if os.path.exists(res_dir):
            shutil.rmtree(res_dir)
        os.mkdir(res_dir)
        count = 0
        print("\n\nNow printing top {} matched Images and their matching scores".format(m))
        for key, value in sorted(rank_dict.items(), key=lambda item: item[1]):
            if count < m:
                print(key + " has matching score:: " + str(value))
                shutil.copy(os.path.join(head, key), res_dir)
                count += 1
            else:
                break


    def LabelLatentSemantic(self, label, model, k):

        model = "bag_" + model
        if label == "left" or label == "right":
            search = "Orientation"
        elif label == "dorsal" or label == "palmar":
            search = "aspectOfHand"
        elif label == "Access" or label == "NoAccess":
            search = "accessories"
        elif label == "male" or label == "female":
            search = "gender"
        else:
            print("Please provide correct label")
            exit(1)

        feature_desc = []
        img_list = []
        imageslist_Meta = []

        for descriptor in imagedb.ImageMetadata.find():
            if descriptor[search] == label:
                imageslist_Meta.append(descriptor["imageName"])

        print(len(imageslist_Meta))

        for descriptor in imagedb.image_models.find():
            if descriptor["_id"] in imageslist_Meta:
                feature_desc.append(descriptor[model])
                img_list.append(descriptor["_id"])

        print(len(img_list))
        svd1 = TruncatedSVD(k)

        feature_desc_transformed = svd1.fit_transform(feature_desc)
        U, S, V = svd(feature_desc, full_matrices=False)

        for i in range(k):
            col = U[:, i]
            arr = []
            for k, val in enumerate(col):
                arr.append((str(img_list[k]), val))
            arr.sort(key=lambda x: x[1], reverse=True)
            print("Printing term-weight pair for latent Symantic {}({}):".format(i + 1, S[i]))
            print(arr)

        return feature_desc_transformed

    def mSimilarImage_Label(self, imgLoc, label, model, k, m):

        if label == "left" or label == "right":
            search = "Orientation"
        elif label == "dorsal" or label == "palmar":
            search = "aspectOfHand"
        elif label == "Access" or label == "NoAccess":
            search = "accessories"
            if label == "Access":
                label = 1
            else:
                label = 0

        elif label == "male" or label == "female":
            search = "gender"
        else:
            print("Please provide correct label")
            exit(1)

        svd = TruncatedSVD(k)
        model = "bag_" + model
        img_list = []
        imageslist_Meta = []
        feature_desc = []

        for descriptor in imagedb.ImageMetadata.find():
            if descriptor[search] == label:
                imageslist_Meta.append(descriptor["imageName"])

        print(len(imageslist_Meta))

        for descriptor in imagedb.image_models.find():
            if descriptor["_id"] in imageslist_Meta:
                feature_desc.append(descriptor[model])
                img_list.append(descriptor["_id"])

        feature_desc_transformed = svd.fit_transform(feature_desc)

        head, tail = os.path.split(imgLoc)

        id = img_list.index(tail)

        rank_dict = {}
        for i, row in enumerate(feature_desc_transformed):
            if (i == id):
                continue
            euc_dis = np.square(np.subtract(feature_desc_transformed[id], feature_desc_transformed[i]))
            match_score = np.sqrt(euc_dis.sum(0))
            rank_dict[img_list[i]] = match_score

        res_dir = os.path.join('..', 'output', model[4:], 'match')
        if os.path.exists(res_dir):
            shutil.rmtree(res_dir)
        os.mkdir(res_dir)
        count = 0
        print("\n\nNow printing top {} matched Images and their matching scores".format(m))
        for key, value in sorted(rank_dict.items(), key=lambda item: item[1]):
            if count < m:
                print(key + " has matching score:: " + str(value))
                shutil.copy(os.path.join(head, key), res_dir)
                count += 1
            else:
                break

    def ImageClassfication(self, imgLoc, model, k ):
        result = {}
        model = "bag_" + model
        head, tail = os.path.split(imgLoc)
        query_desc = []
        for descriptor in imagedb.image_models.find():
            if descriptor["_id"] == tail:
                query_desc.append(descriptor[model])

        labels = ["dorsal", "palmar", "left", "right", "Access", "NoAccess", "male", "female"]

        for label in labels:
            # print(label)

            if label == "left" or label == "right":
                search = "Orientation"
            elif label == "dorsal" or label == "palmar":
                search = "aspectOfHand"
            elif label == "Access" or label == "NoAccess":
                search = "accessories"
                if label == "Access":
                    label = 1
                else:
                    label = 0
            elif label == "male" or label == "female":
                search = "gender"
            else:
                print("Please provide correct label")
                exit(1)

            img_list = []
            imageslist_Meta = []
            frames = []

            for descriptor in imagedb.ImageMetadata.find():
                if search == "Orientation" and descriptor["aspectOfHand"] =="palmar":
                    if descriptor[search] != label:
                        imageslist_Meta.append(descriptor["imageName"])
                    continue
                if descriptor[search] == label:
                    imageslist_Meta.append(descriptor["imageName"])

            # print(len(imageslist_Meta))

            for descriptor in imagedb.image_models.find():
                if descriptor["_id"] in imageslist_Meta and descriptor["_id"] != tail:
                    frames.append(descriptor[model])
                    img_list.append(descriptor["_id"])

            svd = TruncatedSVD(k)
            feature_desc_transformed = svd.fit_transform(frames)
            query_desc_transformed = svd.transform(query_desc)
            mean_transformed = np.true_divide(feature_desc_transformed.sum(0), len(img_list))

            all_dist = []

            # for D_des in feature_desc_transformed:
            #     distance = np.linalg.norm(D_des - query_desc_transformed)
            #     all_dist.append(distance)
            # min_dist = min(all_dist)

            min_dist = np.linalg.norm(mean_transformed - query_desc_transformed)

            result[label] = min_dist


        flag = False
        if result["dorsal"] > result["palmar"]:
            flag = True
            print("palmar")
        else:
            print("dorsal")

        if result["left"] > result["right"]:
            if flag:
                print("Left")
            else:
                print("Right")
        else:
            if flag:
                print("Right")
            else:
                print("Left")

        if result[1] > result[0]:
            print("NoAccess")
        else:
            print("Access")

        if result["male"] > result["female"]:
            print("female")
        else:
            print("male")