import 'package:collaborative_science_platform/models/user.dart';

class Node {
  int id;
  String nodeTitle;
  String publishDate;
  List<User> contributors;
  Node({
    required this.contributors,
    required this.id,
    required this.nodeTitle,
    required this.publishDate,
  });
  factory Node.fromJson(Map<String, dynamic> jsonString) {
    var list = jsonString['authors'] as List;
    List<User> contributors = list.map((e) => User.fromJson(e)).toList();
    return Node(
        id: jsonString['id'],
        nodeTitle: jsonString['title'],
        publishDate: jsonString['date'],
        contributors: contributors);
  }
}

class ProfileData {
  String name;
  String surname;
  String email;
  String aboutMe;
  List<Node> nodes;
  List<int> askedQuestionIDs;
  List<int> answeredQuestionIDs;
  ProfileData(
      {this.aboutMe = "",
      this.email = "",
      this.name = "",
      this.surname = "",
      this.nodes = const [],
      this.askedQuestionIDs = const [],
      this.answeredQuestionIDs = const []});
  factory ProfileData.fromJson(Map<String, dynamic> jsonString) {
    var list = jsonString['nodes'] as List;
    List<Node> nodes = list.map((e) => Node.fromJson(e)).toList();
    return ProfileData(
      nodes: nodes,
      name: jsonString['name'],
      surname: jsonString['surname'],
      aboutMe: jsonString['bio'],
    );
  }

  static getLoremIpsum(int id) {
    return ProfileData(
      name: "Lorem",
      surname: "Ipsum $id",
      email: "loremipsum$id@email.com",
      aboutMe:
          "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
      nodes: [
        Node(
          id: 1,
          nodeTitle: "Lorem Ipsum",
          publishDate: "01.01.2021",
          contributors: [
            User(
              firstName: "Lorem",
              lastName: "Ipsum $id",
              email: "loremipsum$id@email.com",
            ),
          ],
        ),
      ],
      askedQuestionIDs: [1, 2, 3, 4, 5],
      answeredQuestionIDs: [1, 2, 3, 4, 5],
    );
  }
}